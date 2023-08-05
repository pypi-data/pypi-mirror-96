"""
Defines a solver using :mod:`scipy.integrate`
   
.. codeauthor:: David Zwicker <david.zwicker@ds.mpg.de> 
"""

from typing import Callable

import numpy as np

from ..fields.base import FieldBase
from ..pdes.base import PDEBase
from .base import SolverBase


class ScipySolver(SolverBase):
    """class for solving partial differential equations using scipy

    This class is a thin wrapper around :func:`scipy.integrate.solve_ivp`. In
    particular, it supports all the methods implemented by this function.
    """

    name = "scipy"

    def __init__(self, pde: PDEBase, backend: str = "auto", **kwargs):
        r"""
        Args:
            pde (:class:`~pde.pdes.base.PDEBase`):
                The instance describing the pde that needs to be solved
            backend (str):
                Determines how the function is created. Accepted  values are
                'numpy` and 'numba'. Alternatively, 'auto' lets the code decide
                for the most optimal backend.
            **kwargs:
                All extra arguments are forwarded to
                :func:`scipy.integrate.solve_ivp`.
        """
        super().__init__(pde)
        self.backend = backend
        self.solver_params = kwargs

    def make_stepper(
        self, state: FieldBase, dt: float = None
    ) -> Callable[[FieldBase, float, float], float]:
        """return a stepper function

        Args:
            state (:class:`~pde.fields.FieldBase`):
                An example for the state from which the grid and other
                information can be extracted
            dt (float):
                Initial time step for the simulation. If `None`, the solver will
                choose a suitable initial value

        Returns:
            Function that can be called to advance the `state` from time
            `t_start` to time `t_end`. The function call signature is
            `(state: numpy.ndarray, t_start: float, t_end: float)`
        """
        if self.pde.is_sde:
            raise RuntimeError("Cannot use scipy stepper with stochastic equation")

        from scipy import integrate

        shape = state.data.shape
        self.info["dt"] = dt
        self.info["steps"] = 0
        self.info["stochastic"] = False

        # obtain function for evaluating the right hand side
        rhs = self._make_pde_rhs(state, backend=self.backend)

        def rhs_helper(t: float, state_flat: np.ndarray) -> np.ndarray:
            """ helper function to provide the correct call convention """
            return rhs(state_flat.reshape(shape), t).flat  # type: ignore

        def stepper(state: FieldBase, t_start: float, t_end: float) -> float:
            """use scipy.integrate.odeint to advance `state` from `t_start` to
            `t_end`"""
            if dt is not None:
                self.solver_params["first_step"] = min(t_end - t_start, dt)

            sol = integrate.solve_ivp(
                rhs_helper,
                t_span=(t_start, t_end),
                y0=state.data.flat,
                t_eval=[t_end],  # only store necessary
                **self.solver_params,
            )
            self.info["steps"] += sol.nfev
            state.data[:] = sol.y.reshape(shape)
            return sol.t[0]  # type: ignore

        if dt:
            self._logger.info(
                f"Initialized {self.__class__.__name__} stepper with dt=%g", dt
            )
        else:
            self._logger.info(f"Initialized {self.__class__.__name__} stepper")
        return stepper
