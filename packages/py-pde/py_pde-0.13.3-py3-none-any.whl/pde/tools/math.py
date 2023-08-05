"""
Auxiliary mathematical functions

.. codeauthor:: David Zwicker <david.zwicker@ds.mpg.de>
"""

from typing import Tuple

import numpy as np


class SmoothData1D:
    """allows smoothing data in 1d using a Gaussian kernel of defined width

    The data is given a pairs of `x` and `y`, the assumption being that there is
    an underlying relation `y = f(x)`.
    """

    sigma_auto_scale: float = 10
    """ float: scale for setting automatic values for sigma """

    def __init__(self, x, y, sigma: float = None):
        """initialize with data

        Args:
            x: List of x values
            y: List of y values
            sigma (float): The size of the smoothing window using units of `x`.
                If it is not given, the average distance of x values multiplied
                by `sigma_auto_scale` is used.
        """
        self.x = np.ravel(x)
        self.y = np.ravel(y)
        if self.x.shape != self.y.shape:
            raise ValueError("`x` and `y` must have equal number of elements")

        if sigma is None:
            self.sigma = float(self.sigma_auto_scale * self.x.ptp() / len(self.x))
        else:
            self.sigma = sigma

    @property
    def bounds(self) -> Tuple[float, float]:
        """ return minimal and maximal `x` values """
        return float(self.x.min()), float(self.x.max())

    def __call__(self, xs):
        """return smoothed y values for the positions given in `xs`

        Args:
            xs: a list of x-values

        Returns:
            :class:`~numpy.ndarray`: The associated y-values
        """
        xs = np.asanyarray(xs)
        shape = xs.shape
        xs = np.ravel(xs)
        scale = 0.5 * self.sigma ** -2

        with np.errstate(under="ignore"):
            weight = np.exp(-scale * (self.x[:, None] - xs[None, :]) ** 2)
            weight /= weight.sum(axis=0)
        result = np.dot(self.y, weight)
        return result.reshape(shape)
