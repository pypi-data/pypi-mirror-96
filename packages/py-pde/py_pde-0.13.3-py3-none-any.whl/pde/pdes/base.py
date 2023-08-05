"""
Base classes
   
.. codeauthor:: David Zwicker <david.zwicker@ds.mpg.de> 
"""

import logging
from abc import ABCMeta, abstractmethod
from typing import Optional  # @UnusedImport
from typing import TYPE_CHECKING, Any, Callable, Dict, Tuple, Union

import numpy as np

from ..fields import FieldCollection
from ..fields.base import FieldBase
from ..tools.numba import jit
from ..tools.typing import ArrayLike
from ..trackers.base import TrackerCollectionDataType

if TYPE_CHECKING:
    from ..solvers.controller import TRangeType  # @UnusedImport


class PDEBase(metaclass=ABCMeta):
    """base class for solving partial differential equations

    Custom PDEs can be implemented by specifying their evolution rate. In the
    simple case of deterministic PDEs, the methods
    :meth:`PDEBase.evolution_rate` and :meth:`PDEBase._make_pde_rhs_numba` need
    to be overwritten for the `numpy` and `numba` backend, respectively.
    """

    check_implementation: bool = True
    """ bool: Flag determining whether (some) numba-compiled functions should be
    checked against their numpy counter-parts. This can help with implementing a
    correct compiled version for a PDE class. """

    explicit_time_dependence: Optional[bool] = None
    """ bool: Flag indicating whether the right hand side of the PDE has an
    explicit time dependence. """

    complex_valued: bool = False
    """ bool: Flag indicating whether the right hand side is a complex-valued PDE, which
    requires all involved variables to be of complex type """

    def __init__(self, noise: ArrayLike = 0):
        """
        Args:
            noise (float or :class:`~numpy.ndarray`):
                Magnitude of the additive Gaussian white noise that is supported for all
                PDEs by default. If set to zero, a deterministic partial differential
                equation will be solved. Different noise magnitudes can be supplied for
                each field in coupled PDEs.

        Note:
            If more complicated noise structures are required, the methods
            :meth:`PDEBase.noise_realization` and
            :meth:`PDEBase._make_noise_realization_numba` need to be overwritten
            for the `numpy` and `numba` backend, respectively.
        """
        self._logger = logging.getLogger(self.__class__.__name__)
        self.noise = noise

    @property
    def is_sde(self) -> bool:
        """flag indicating whether this is a stochastic differential equation

        The :class:`BasePDF` class supports additive Gaussian white noise, whose
        magnitude is controlled by the `noise` property. In this case, `is_sde`
        is `True` if `self.noise != 0`.
        """
        # check for self.noise, in case __init__ is not called in a subclass
        return hasattr(self, "noise") and np.any(np.asarray(self.noise) != 0)  # type: ignore

    def make_modify_after_step(self, state: FieldBase) -> Callable[[np.ndarray], float]:
        """returns a function that can be called to modify a state

        This function is applied to the state after each integration step when
        an explicit stepper is used. The default behavior is to not change the
        state.

        Args:
            state (:class:`~pde.fields.FieldBase`):
                An example for the state from which the grid and other information can
                be extracted

        Returns:
            Function that can be applied to a state to modify it and which
            returns a measure for the corrections applied to the state
        """

        def modify_after_step(state_data: np.ndarray) -> float:
            """ no-op function """
            return 0

        return modify_after_step

    @abstractmethod
    def evolution_rate(self, state: FieldBase, t: float = 0) -> FieldBase:
        pass

    def _make_pde_rhs_numba(
        self, state: FieldBase
    ) -> Callable[[np.ndarray, float], np.ndarray]:
        """ create a compiled function for evaluating the right hand side """
        raise NotImplementedError

    def make_pde_rhs(
        self, state: FieldBase, backend: str = "auto"
    ) -> Callable[[np.ndarray, float], np.ndarray]:
        """return a function for evaluating the right hand side of the PDE

        Args:
            state (:class:`~pde.fields.FieldBase`):
                An example for the state from which the grid and other
                information can be extracted
            backend (str): Determines how the function is created. Accepted
                values are 'python` and 'numba'. Alternatively, 'auto' lets the
                code decide for the most optimal backend.

        Returns:
            Function determining the right hand side of the PDE
        """
        if backend == "auto":
            try:
                rhs = self._make_pde_rhs_numba(state)
            except NotImplementedError:
                backend = "numpy"
            else:
                rhs._backend = "numba"  # type: ignore

        if backend == "numba":
            rhs = self._make_pde_rhs_numba(state)
            rhs._backend = "numba"  # type: ignore

        elif backend == "numpy":
            state = state.copy()

            def evolution_rate_numpy(state_data: np.ndarray, t: float) -> np.ndarray:
                """ evaluate the rhs given only a state without the grid """
                state.data = state_data
                return self.evolution_rate(state, t).data

            rhs = evolution_rate_numpy
            rhs._backend = "numpy"  # type: ignore

        elif backend != "auto":
            raise ValueError(
                f"Unknown backend `{backend}`. Possible values are ['auto', 'numpy', "
                "'numba']"
            )

        if self.check_implementation and rhs._backend == "numba":  # type: ignore
            # obtain and check result from the numpy implementation
            rhs_numpy = self.evolution_rate(state.copy(), 0).data
            if not np.all(np.isfinite(rhs_numpy)):
                self._logger.warning(
                    "The numpy implementation of the PDE returned non-finite values."
                )

            # obtain and check result from the numba implementation
            test_state = state.copy()
            rhs_numba = rhs(test_state.data, 0)
            if not np.all(np.isfinite(rhs_numba)):
                self._logger.warning(
                    "The numba implementation of the PDE returned non-finite values."
                )

            # compare the two implementations
            msg = (
                "The numba compiled implementation of the right hand side is not "
                "compatible with the numpy implementation. This check can be disabled "
                "by setting the class attribute `check_implementation` to `False`."
            )
            np.testing.assert_allclose(
                rhs_numba, rhs_numpy, err_msg=msg, rtol=1e-7, atol=1e-7, equal_nan=True
            )

        return rhs

    def noise_realization(
        self, state: FieldBase, t: float = 0, label: str = "Noise realization"
    ) -> FieldBase:
        """returns a realization for the noise

        Args:
            state (:class:`~pde.fields.ScalarField`):
                The scalar field describing the concentration distribution
            t (float):
                The current time point
            label (str):
                The label for the returned field

        Returns:
            :class:`~pde.fields.ScalarField`:
            Scalar field describing the evolution rate of the PDE
        """
        if self.noise:
            if np.isscalar(self.noise):
                # a single noise value is given for all fields
                data = np.random.normal(scale=self.noise, size=state.data.shape)
                return state.copy(data=data, label=label)

            elif isinstance(state, FieldCollection):
                # different noise strengths, assuming one for each field
                fields = []
                for f, n in zip(state, np.broadcast_to(self.noise, len(state))):
                    if n == 0:
                        data = 0
                    else:
                        data = np.random.normal(scale=n, size=f.data.shape)
                    fields.append(f.copy(data=data))
                return FieldCollection(fields, label=label)

            else:
                # different noise strengths, but a single field
                raise RuntimeError(
                    f"Multiple noise strengths were given for the single field {state}"
                )

        else:
            return state.copy(data=0, label=label)

    def _make_noise_realization_numba(
        self, state: FieldBase
    ) -> Callable[[np.ndarray, float], np.ndarray]:
        """return a function for evaluating the noise term of the PDE

        Args:
            state (:class:`~pde.fields.FieldBase`):
                An example for the state from which the grid and other
                information can be extracted

        Returns:
            Function determining the right hand side of the PDE
        """
        if self.noise:
            data_shape = state.data.shape

            if np.isscalar(self.noise):
                # a single noise value is given for all fields
                noise_strength = float(self.noise)  # type: ignore

                @jit
                def noise_realization(state_data: np.ndarray, t: float) -> np.ndarray:
                    """ helper function returning a noise realization """
                    return noise_strength * np.random.randn(*data_shape)  # type: ignore

            elif isinstance(state, FieldCollection):
                # different noise strengths, assuming one for each field
                noise_strengths = np.empty(data_shape[0])
                noise_arr = np.broadcast_to(self.noise, len(state))
                for i, noise in enumerate(noise_arr):
                    noise_strengths[state._slices[i]] = noise

                @jit
                def noise_realization(state_data: np.ndarray, t: float) -> np.ndarray:
                    """ helper function returning a noise realization """
                    out = np.random.randn(*data_shape)
                    for i in range(data_shape[0]):
                        # TODO: Avoid creating random numbers when noise_strengths == 0
                        out[i] *= noise_strengths[i]
                    return out  # type: ignore

            else:
                # different noise strengths, but a single field
                raise RuntimeError(
                    f"Multiple noise strengths were given for the single field {state}"
                )

        else:

            @jit
            def noise_realization(state_data: np.ndarray, t: float) -> None:
                """ helper function returning a noise realization """
                return None

        return noise_realization  # type: ignore

    def _make_sde_rhs_numba(
        self, state: FieldBase
    ) -> Callable[[np.ndarray, float], Tuple[np.ndarray, np.ndarray]]:
        """return a function for evaluating the noise term of the PDE

        Args:
            state (:class:`~pde.fields.FieldBase`):
                An example for the state from which the grid and other
                information can be extracted

        Returns:
            Function determining the right hand side of the PDE
        """
        evolution_rate = self._make_pde_rhs_numba(state)
        noise_realization = self._make_noise_realization_numba(state)

        @jit
        def sde_rhs(state_data: np.ndarray, t: float) -> Tuple[np.ndarray, np.ndarray]:
            """ compiled helper function returning a noise realization """
            return (evolution_rate(state_data, t), noise_realization(state_data, t))

        return sde_rhs  # type: ignore

    def make_sde_rhs(
        self, state: FieldBase, backend: str = "auto"
    ) -> Callable[[np.ndarray, float], Tuple[np.ndarray, np.ndarray]]:
        """return a function for evaluating the right hand side of the SDE

        Args:
            state (:class:`~pde.fields.FieldBase`):
                An example for the state from which the grid and other
                information can be extracted
            backend (str): Determines how the function is created. Accepted
                values are 'python` and 'numba'. Alternatively, 'auto' lets the
                code decide for the most optimal backend.

        Returns:
            Function determining the deterministic part of the right hand side
            of the PDE together with a noise realization.
        """
        if backend == "auto":
            try:
                sde_rhs = self._make_sde_rhs_numba(state)
            except NotImplementedError:
                backend = "numpy"
            else:
                sde_rhs._backend = "numba"  # type: ignore
                return sde_rhs

        if backend == "numba":
            sde_rhs = self._make_sde_rhs_numba(state)
            sde_rhs._backend = "numba"  # type: ignore

        elif backend == "numpy":
            state = state.copy()

            def sde_rhs(
                state_data: np.ndarray, t: float
            ) -> Tuple[np.ndarray, np.ndarray]:
                """ evaluate the rhs given only a state without the grid """
                state.data = state_data
                return (
                    self.evolution_rate(state, t).data,
                    self.noise_realization(state, t).data,
                )

            sde_rhs._backend = "numpy"  # type: ignore

        else:
            raise ValueError(f"Unknown backend `{backend}`")

        return sde_rhs

    def solve(
        self,
        state: FieldBase,
        t_range: "TRangeType",
        dt: float = None,
        tracker: TrackerCollectionDataType = ["progress", "consistency"],
        method: str = "auto",
        ret_info: bool = False,
        **kwargs,
    ) -> Union[FieldBase, Tuple[FieldBase, Dict[str, Any]]]:
        """convenience method for solving the partial differential equation

        The method constructs a suitable solver
        (:class:`~pde.solvers.base.SolverBase`) and controller
        (:class:`~pde.controller.Controller`) to advance the state over the
        temporal range specified by `t_range`. To obtain full flexibility, it is
        advisable to construct these classes explicitly.

        Args:
            state (:class:`~pde.fields.base.FieldBase`):
                The initial state (which also defines the grid)
            t_range (float or tuple):
                Sets the time range for which the PDE is solved. If only a
                single value `t_end` is given, the time range is assumed to be
                `[0, t_end]`.
            dt (float):
                Time step of the chosen stepping scheme. If `None`, a default
                value based on the stepper will be chosen.
            tracker:
                Defines a tracker that process the state of the simulation at
                fixed time intervals. Multiple trackers can be specified as a
                list. The default value is ['progress', 'consistency'], which
                displays a progress bar and checks the state for consistency,
                aborting the simulation when not-a-number values appear.
            method (:class:`~pde.solvers.base.SolverBase` or str):
                Specifies a method for solving the differential equation. This
                can either be an instance of
                :class:`~pde.solvers.base.SolverBase` or a descriptive name
                like 'explicit' or 'scipy'. The valid names are given by
                :meth:`pde.solvers.base.SolverBase.registered_solvers`.
            ret_info (bool):
                Flag determining whether diagnostic information about the solver
                process should be returned.
            **kwargs:
                Additional keyword arguments are forwarded to the solver class

        Returns:
            :class:`~pde.fields.base.FieldBase`:
            The state at the final time point. In the case `ret_info == True`, a
            tuple with the final state and a dictionary with additional
            information is returned.
        """
        from ..solvers.base import SolverBase

        if method == "auto":
            method = "scipy" if dt is None else "explicit"

        # create solver
        if callable(method):
            solver = method(pde=self, **kwargs)
            if not isinstance(solver, SolverBase):
                self._logger.warn(
                    "Solver is not an instance of `SolverBase`. Specified wrong method?"
                )
        else:
            solver = SolverBase.from_name(method, pde=self, **kwargs)

        # create controller
        from ..solvers import Controller

        controller = Controller(solver, t_range=t_range, tracker=tracker)

        # run the simulation
        final_state = controller.run(state, dt)

        if ret_info:
            info = controller.info.copy()
            info.pop("solver_class")  # remove redundant information
            info["solver"] = solver.info.copy()
            return final_state, info
        else:
            return final_state


def expr_prod(factor: float, expression: str) -> str:
    """helper function for building an expression with an (optional) pre-factor

    Args:
        factor (float): The value of the prefactor
        expression (str): The remaining expression

    Returns:
        str: The expression with the factor appended if necessary
    """
    if factor == 0:
        return "0"
    elif factor == 1:
        return expression
    elif factor == -1:
        return "-" + expression
    else:
        return f"{factor:g} * {expression}"
