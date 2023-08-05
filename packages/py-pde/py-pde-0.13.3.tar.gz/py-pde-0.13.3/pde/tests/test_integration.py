"""
Integration tests that use multiple modules together

.. codeauthor:: David Zwicker <david.zwicker@ds.mpg.de>
"""

import numpy as np

from pde import CartesianGrid, DiffusionPDE, FileStorage, ScalarField, UnitGrid
from pde.tools.misc import skipUnlessModule


@skipUnlessModule("h5py")
def test_writing_to_storage(tmp_path):
    """ test whether data is written to storage """
    state = ScalarField.random_uniform(UnitGrid([3]))
    pde = DiffusionPDE()
    path = tmp_path / "test_writing_to_storage.hdf5"
    data = FileStorage(filename=path)
    pde.solve(state, t_range=1.1, dt=0.1, tracker=[data.tracker(0.5)])

    assert len(data) == 3


def test_inhomogeneous_bcs():
    """ test simulation with inhomogeneous boundary conditions """
    # single coordinate
    grid = CartesianGrid([[0, 2 * np.pi], [0, 1]], [32, 2], periodic=[True, False])
    state = ScalarField(grid)
    pde = DiffusionPDE(bc=["natural", {"type": "value", "value": "sin(x)"}])
    sol = pde.solve(state, t_range=1e1, dt=1e-2, tracker=None)
    data = sol.get_line_data(extract="project_x")
    np.testing.assert_almost_equal(
        data["data_y"], 0.9 * np.sin(data["data_x"]), decimal=2
    )

    # double coordinate
    grid = CartesianGrid([[0, 1], [0, 1]], [8, 8], periodic=False)
    state = ScalarField(grid)
    pde = DiffusionPDE(bc={"type": "value", "value": "x + y"})
    sol = pde.solve(state, t_range=1e1, dt=1e-3, tracker=None)
    expect = ScalarField.from_expression(grid, "x + y")
    np.testing.assert_almost_equal(sol.data, expect.data)
