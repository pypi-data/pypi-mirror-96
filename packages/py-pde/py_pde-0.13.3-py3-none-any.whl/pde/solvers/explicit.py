"""
Defines an explicit solver supporting various methods
   
.. codeauthor:: David Zwicker <david.zwicker@ds.mpg.de> 
"""

from typing import Callable, Tuple

import numpy as np

from ..fields.base import FieldBase
from ..pdes.base import PDEBase
from ..tools.numba import jit
from .base import SolverBase


class ExplicitSolver(SolverBase):
    """ class for solving partial differential equations explicitly """

    name = "explicit"

    def __init__(self, pde: PDEBase, scheme: str = "euler", backend: str = "auto"):
        """
        Args:
            pde (:class:`~pde.pdes.base.PDEBase`):
                The instance describing the pde that needs to be solved
            scheme (str):
                Defines the explicit scheme to use. Supported values are
                'euler', 'runge-kutta' (or 'rk' for short).
            backend (str):
                Determines how the function is created. Accepted  values are
                'numpy` and 'numba'. Alternatively, 'auto' lets the code decide
                for the most optimal backend.
        """
        super().__init__(pde)
        self.scheme = scheme
        self.backend = backend

    def _make_euler_stepper(
        self, state: FieldBase, dt: float
    ) -> Callable[[np.ndarray, float, int], Tuple[float, float]]:
        """make a simple Euler stepper

        Args:
            state (:class:`~pde.fields.FieldBase`):
                An example for the state from which the grid and other
                information can be extracted
            dt (float):
                Time step of the explicit stepping. If `None`, this solver
                specifies 1e-3 as a default value.

        Returns:
            Function that can be called to advance the `state` from time
            `t_start` to time `t_end`. The function call signature is
            `(state: numpy.ndarray, t_start: float, t_end: float)`
        """

        # obtain post-step action function
        modify_after_step = jit(self.pde.make_modify_after_step(state))

        if self.pde.is_sde:
            # handle stochastic version of the pde

            rhs_sde = self._make_sde_rhs(state, backend=self.backend)

            def stepper(
                state_data: np.ndarray, t_start: float, steps: int
            ) -> Tuple[float, float]:
                """ compiled inner loop for speed """
                modifications = 0.0
                for i in range(steps):
                    # calculate the right hand side
                    t = t_start + i * dt
                    evolution_rate, noise_realization = rhs_sde(state_data, t)
                    state_data += dt * evolution_rate
                    if noise_realization is not None:
                        state_data += np.sqrt(dt) * noise_realization
                    modifications += modify_after_step(state_data)

                return t + dt, modifications

            self.info["stochastic"] = True
            self._logger.info(
                f"Initialized explicit Euler-Maruyama stepper with dt=%g", dt
            )

        else:
            # handle deterministic  version of the pde
            rhs_pde = self._make_pde_rhs(state, backend=self.backend)

            def stepper(
                state_data: np.ndarray, t_start: float, steps: int
            ) -> Tuple[float, float]:
                """ compiled inner loop for speed """
                modifications = 0
                for i in range(steps):
                    # calculate the right hand side
                    t = t_start + i * dt
                    state_data += dt * rhs_pde(state_data, t)
                    modifications += modify_after_step(state_data)

                return t + dt, modifications

            self.info["stochastic"] = False
            self._logger.info(f"Initialized explicit Euler stepper with dt=%g", dt)

        return stepper

    def _make_rk45_stepper(
        self, state: FieldBase, dt: float
    ) -> Callable[[np.ndarray, float, int], Tuple[float, float]]:
        """make a simple stepper for the explicit Runge-Kutta method of order 5(4)

        Args:
            state (:class:`~pde.fields.FieldBase`):
                An example for the state from which the grid and other
                information can be extracted
            dt (float):
                Time step of the explicit stepping. If `None`, this solver
                specifies 1e-3 as a default value.

        Returns:
            Function that can be called to advance the `state` from time
            `t_start` to time `t_end`. The function call signature is
            `(state: numpy.ndarray, t_start: float, t_end: float)`
        """
        if self.pde.is_sde:
            raise RuntimeError(
                "Cannot use Runge-Kutta stepper with stochastic equation"
            )

        rhs = self._make_pde_rhs(state, backend=self.backend)
        self.info["stochastic"] = False

        # obtain post-step action function
        modify_after_step = jit(self.pde.make_modify_after_step(state))

        def stepper(
            state_data: np.ndarray, t_start: float, steps: int
        ) -> Tuple[float, float]:
            """ compiled inner loop for speed """
            modifications = 0
            for i in range(steps):
                # calculate the right hand side
                t = t_start + i * dt

                # calculate the intermediate values in Runge-Kutta
                k1 = dt * rhs(state_data, t)
                k2 = dt * rhs(state_data + 0.5 * k1, t + 0.5 * dt)
                k3 = dt * rhs(state_data + 0.5 * k2, t + 0.5 * dt)
                k4 = dt * rhs(state_data + k3, t + dt)

                state_data += (k1 + 2 * k2 + 2 * k3 + k4) / 6
                modifications += modify_after_step(state_data)

            return t + dt, modifications

        self._logger.info(f"Initialized explicit Runge-Kutta-45 stepper with dt=%g", dt)
        return stepper

    def make_stepper(
        self, state: FieldBase, dt=None
    ) -> Callable[[FieldBase, float, float], float]:
        """return a stepper function using an explicit scheme

        Args:
            state (:class:`~pde.fields.FieldBase`):
                An example for the state from which the grid and other
                information can be extracted
            dt (float):
                Time step of the explicit stepping. If `None`, this solver
                specifies 1e-3 as a default value.

        Returns:
            Function that can be called to advance the `state` from time
            `t_start` to time `t_end`. The function call signature is
            `(state: numpy.ndarray, t_start: float, t_end: float)`
        """
        # support `None` as a default value, so the controller can signal that
        # the solver should use a default time step
        if dt is None:
            dt = 1e-3

        self.info["dt"] = dt
        self.info["steps"] = 0
        self.info["scheme"] = self.scheme
        self.info["state_modifications"] = 0.0

        if self.scheme == "euler":
            inner_stepper = self._make_euler_stepper(state, dt)
        elif self.scheme in {"runge-kutta", "rk", "rk45"}:
            inner_stepper = self._make_rk45_stepper(state, dt)
        else:
            raise ValueError(f"Explicit scheme {self.scheme} is not supported")

        if self.info["backend"] == "numba":
            # compile inner step
            inner_stepper = jit(inner_stepper)

        def stepper(state: FieldBase, t_start: float, t_end: float) -> float:
            """ use Euler stepping to advance `state` from `t_start` to `t_end` """
            # calculate number of steps (which is at least 1)
            steps = max(1, int(np.ceil((t_end - t_start) / dt)))
            t_last, modifications = inner_stepper(state.data, t_start, steps)
            self.info["steps"] += steps
            self.info["state_modifications"] += modifications
            return t_last

        return stepper
