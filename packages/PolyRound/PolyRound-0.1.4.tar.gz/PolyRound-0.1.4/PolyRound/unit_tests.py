import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
# print(sys.path[0])
sys.path.insert(0, os.getcwd())
from PolyRound.static_classes.lp_utils import ChebyshevFinder
from PolyRound.static_classes.hdf5_csv_io import HDF5
import numpy as np
from PolyRound.static_classes.lp_interfacing import OptlangInterfacer
from PolyRound.static_classes.constraint_removal_reduction import PolytopeReducer
from PolyRound.static_classes.rounding.maximum_volume_ellipsoid import (
    MaximumVolumeEllipsoidFinder,
)
from PolyRound.static_classes.rounding.nearest_symmetric_positive_definite import NSPD
from PolyRound.static_classes.rounding.geometric_mean_scaling import (
    geometric_mean_scaling,
)
from PolyRound.mutable_classes.polytope import Polytope
from PolyRound.static_classes.parse_sbml_stoichiometry import StoichiometryParser
from PolyRound.api import PolyRoundApi
import pandas as pd


class TestHDF5IO(unittest.TestCase):
    def test_reading(self):
        polytope1 = StoichiometryParser.parse_sbml_cobrapy(
            "PolyRound/models/e_coli_core.xml"
        )
        filename = "PolyRound/output/temp.hdf5"
        HDF5.polytope_to_h5(polytope1, filename)
        polytope2 = HDF5.h5_to_polytope(filename)
        for attribute in dir(polytope1):
            tentative_df1 = getattr(polytope1, attribute)
            tentative_df2 = getattr(polytope2, attribute)
            if isinstance(tentative_df1, pd.DataFrame) or isinstance(
                tentative_df1, pd.Series
            ):
                test = tentative_df1.equals(tentative_df2)
                self.assertTrue(test)


class TestRounding(unittest.TestCase):
    def test_solve(self):
        A = np.array([[-1, 0, 0], [0, -1, 0], [0, 0, -1], [1, 1, 1]])
        b = np.array([[0], [0], [0], [1]])
        x = np.array([[0.1], [0.1], [0.1]])

        x, E, converged = MaximumVolumeEllipsoidFinder.run_mve(A, b, x, 1e-3)
        E_sol = np.array(
            [[0.25, 0, 0], [-0.0833, 0.2357, 0], [-0.0833, -0.1178, 0.2042]]
        )
        self.assertTrue(np.allclose(E, E_sol, atol=1e-03))

    def test_solve_coli(self):
        A = np.loadtxt("PolyRound/csvs/A_ineq_e_coli_core_test.csv", delimiter=",")
        b = np.loadtxt("PolyRound/csvs/b_ineq_e_coli_core_test.csv", delimiter=",")[
            :, None
        ]
        E_sol = np.loadtxt("PolyRound/csvs/e_coli_core_mve_test_sol.csv", delimiter=",")
        x = np.zeros((A.shape[1], 1))
        x, E, converged = MaximumVolumeEllipsoidFinder.run_mve(A, b, x, 1e-3)
        diff_mat = np.abs(E_sol - E)
        self.assertLess(np.min(diff_mat), 1e-10)
        pass

    def test_iterative_solve(self):
        A = np.loadtxt("PolyRound/csvs/A_ineq_e_coli_core_test.csv", delimiter=",")
        b = np.loadtxt("PolyRound/csvs/b_ineq_e_coli_core_test.csv", delimiter=",")[
            :, None
        ]
        A_sol = np.loadtxt(
            "PolyRound/csvs/A_e_coli_core_mve_test_reg.csv", delimiter=","
        )
        b_sol = np.loadtxt(
            "PolyRound/csvs/b_e_coli_core_mve_test_reg.csv", delimiter=","
        )
        p = Polytope(A, np.squeeze(b))
        MaximumVolumeEllipsoidFinder.iterative_solve(p, backend="glpk")
        diff_mat = np.abs(p.A.values - A_sol)
        self.assertLess(np.min(diff_mat), 1e-10)
        diff_vec = np.abs(p.b.values - b_sol)
        self.assertLess(np.min(diff_vec), 1e-10)

    def test_geometric_mean_scaling(self):
        A = np.array([[1, 2, 3, 4], [1e1, 1e2, 1e3, 1e4], [1e-1, 1e-2, 1e-3, 1e-4]])
        cscale, rscale = geometric_mean_scaling(A, 0, 0.99)
        cscale_sol = np.array(
            [31.6227766016838, 3.16227766016838, 3.16227766016838, 31.6227766016838]
        )
        rscale_sol = np.array([2.00000000000000, 316.227766016837, 0.00316227766016838])
        r_diff = np.max(rscale - rscale_sol)
        c_diff = np.max(cscale - cscale_sol)
        self.assertLess(r_diff, 1e-10)
        self.assertLess(c_diff, 1e-10)

    def test_NSPD(self):
        A = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        A_sol = np.array([[2, 3, 4], [3, 5, 6], [4, 6, 9]])
        A_hat = NSPD.get_NSPD(A)
        diff = np.max(np.abs(A_hat - A_sol))
        self.assertLess(diff, 1)

    def test_transform(self):
        S = np.zeros((1, 3))
        S[0, :] = 1
        A = pd.DataFrame(np.vstack((np.eye(3), -np.eye(3), S)))
        b = pd.Series(np.array([1, 1, 1, 1, 1, 1, 0], dtype=float))
        x = np.array([4, 9, 83])
        polytope = Polytope(A, b, S=S)
        shift1 = np.array([1, 2, 3])
        transform1 = np.array([[43, 6, 3], [11, 6, 4], [-54, 5, 5431]])
        shift2 = np.array([-5, 3, 0.41])
        transform2 = np.matmul(shift1[:, None], shift2[:, None].T) + np.eye(3)
        x_mod = x.copy()
        x_mod -= shift1
        polytope.apply_shift(shift1)
        x_mod = np.matmul(np.linalg.inv(transform1), x_mod)
        polytope.apply_transformation(transform1)
        self.assertTrue(np.allclose(x, polytope.back_transform(x_mod.copy())))
        x_mod -= shift2
        polytope.apply_shift(shift2)
        self.assertTrue(np.allclose(x, polytope.back_transform(x_mod.copy())))
        x_mod = np.matmul(np.linalg.inv(transform2), x_mod)
        polytope.apply_transformation(transform2)
        self.assertTrue(np.allclose(x, polytope.back_transform(x_mod.copy())))
        shift3 = np.power(shift1, shift2)
        x_mod -= shift3
        polytope.apply_shift(shift3)
        self.assertTrue(np.allclose(x, polytope.back_transform(x_mod.copy())))


class TestCoordinateTransform(unittest.TestCase):
    def setUp(self):
        self.input = "PolyRound/models/e_coli_core.xml"
        self.S_cobra = np.loadtxt("PolyRound/csvs/S_cobra.csv", delimiter=",")
        self.A_cobra = np.loadtxt("PolyRound/csvs/A_cobra.csv", delimiter=",")
        self.b_cobra = np.loadtxt("PolyRound/csvs/b_cobra.csv", delimiter=",")
        # self.options = {"presolve": True, "method": "revised simplex"}

    def test_degenerate_polytope(self):
        S = np.array([[1, 0], [0, 1],])
        A = np.eye(2)
        b = np.ones(2)
        p = Polytope(A, b, S=S)
        self.assertRaises(ValueError, PolyRoundApi.simplify_polytope, p)

    def test_simple_null_space(self):
        S = np.array([[1, -1, 0], [0, 1, -1],])
        null = PolytopeReducer.null_space(S)
        self.assertEqual(null.shape[1], 1)

    def test_keep_equalities(self):
        S = np.array([[1, -1, 0], [0, 1, -1],])
        A = np.array([[0.0, 0.0, 1.0], [0.0, 0.0, -1.0]])
        b = np.array([5.25, 1.75])
        p = Polytope(A, b, S=S)
        p = PolyRoundApi.simplify_transform_and_round(p)
        self.assertTrue(p.transformation.shape == (3, 1))

    def test_interior_point_original(self):
        backend = "glpk"
        polytope = StoichiometryParser.parse_sbml_cobrapy(self.input)

        obj = np.ones(polytope.A.shape[1])
        b_eq = np.zeros(polytope.S.shape[0])
        S = np.array(polytope.S).astype(float)

        A = np.array(polytope.A).astype(float)

        b = np.array(polytope.b).astype(float)
        sol, model = OptlangInterfacer.gurobi_solve(obj, A, b, backend, S=S, h=b_eq)
        self.assertEqual(model.status, "optimal")

    def test_matlab_matrices(self):
        backend = "glpk"
        obj = np.ones(self.S_cobra.shape[1])
        b_eq = np.zeros(self.S_cobra.shape[0])
        sol, model = OptlangInterfacer.gurobi_solve(
            obj, self.A_cobra, self.b_cobra, backend, S=self.S_cobra, h=b_eq
        )
        self.assertEqual(model.status, "optimal")

    def test_compare_python_cobra_matrices(self):

        polytope = StoichiometryParser.parse_sbml_cobrapy(self.input)

        S_cobra = self.S_cobra / 10000

        for col, cob_col in zip(np.transpose(polytope.S.values), np.transpose(S_cobra)):
            sim = col == cob_col
            self.assertTrue(sim.all())

        A_cobra = np.around(self.A_cobra)
        A_cobra = A_cobra.astype(int)
        A = np.array(polytope.A, dtype=int)
        for col, cob_col in zip(np.transpose(A), np.transpose(A_cobra)):
            sim = col == cob_col
            self.assertTrue(sim.all())

        # Now move on to b
        b = np.array(polytope.b)
        b = b.reshape((b.size,))
        bool = self.b_cobra == b
        self.assertTrue(bool.all())

    def test_chebyshev_center(self):
        S = np.zeros((1, 3))
        S[0, :] = 1

        A = pd.DataFrame(np.vstack((np.eye(3), -np.eye(3), S)))
        b = pd.Series(np.array([1, 1, 1, 1, 1, 1, 0], dtype=float))
        x, dist0 = ChebyshevFinder.chebyshev_center(Polytope(A, b))
        self.assertTrue(np.all(np.abs(x - x[0]) < 1e-10))
        self.assertTrue(dist0 > 0)

        b[3] = 0
        x, dist1 = ChebyshevFinder.chebyshev_center(Polytope(A, b))
        self.assertTrue(np.all(x[0] - x[1:] > 0))
        self.assertTrue(dist0 > dist1)

    def test_minimal_lp(self):
        b = np.array([1, 1, 1, 1])
        A_ext = np.array([[1, 0, 1], [0, 1, 1], [-1, 0, 1], [0, -1, 1]])
        obj = np.array([0, 0, -1])
        val, m = OptlangInterfacer.gurobi_solve(obj, A_ext, b, "glpk")
        self.assertTrue(np.all(val == np.array([0, 0, 1])))
        # p = Polytope(A, b)
        # x, dist = ChebyshevFinder.chebyshev_center(p)
        # self.assertTrue(False)

    def test_constraint_removal(self):
        S = np.zeros((1, 3))
        S[0, :] = [0, 0, 1]
        h = np.zeros((S.shape[0],))
        h[0] = 1
        A = np.vstack((-np.eye(3), -np.ones((1, 3)), np.ones((1, 3))))
        b = np.array([1, 1, 1, -1, 1], dtype=float)
        b = b.reshape((5,))
        p = Polytope(pd.DataFrame(A), pd.Series(b), S=pd.DataFrame(S), h=pd.Series(h))
        reduced_polytope, removed, refunctioned = PolytopeReducer.constraint_removal(
            p, dict()
        )
        A_true = np.array([[-1, 0, 0], [0, -1, 0]])
        S_true = np.array([[-1, -1, -1], [0, 0, 1]])
        b_true = [1, 1]
        h_true = [-1, 1]
        self.assertTrue(np.all(reduced_polytope.A == A_true))
        self.assertTrue(np.all(reduced_polytope.S == S_true))
        self.assertTrue(np.all(reduced_polytope.b == b_true))
        self.assertTrue(np.all(reduced_polytope.h == h_true))

    def test_constraint_simplification_non_bounded(self):
        A = np.vstack((-np.eye(3), -np.ones((1, 3))))
        b = np.array([1, 1, 1, 3], dtype=float)
        b = b.reshape((4,))
        p = Polytope(pd.DataFrame(A), pd.Series(b))
        reduced_polytope = PolyRoundApi.simplify_polytope(p)
        A_true = np.array([[-1, 0, 0], [0, -1, 0], [0, 0, -1]])
        b_true = [1, 1, 1]
        self.assertTrue(np.all(reduced_polytope.A == A_true))

        self.assertTrue(np.all(reduced_polytope.b == b_true))

    def test_transformation_coli(self):
        backend = "gurobi"
        # eps is for svd
        eps = 1e-12
        # thresh is for declaring equality constraints
        thresh = 1e-06

        polytope = StoichiometryParser.parse_sbml_cobrapy(self.input)
        polytope.normalize()
        reduced_polytope = PolyRoundApi.simplify_polytope(polytope)

        # compute chebyshev center
        x, dist = ChebyshevFinder.chebyshev_center(
            reduced_polytope,
            backend=backend,
            regularize=backend == "gurobi",
            NumericFocus=3,
            MarkowitzTol=0.999,
            FeasibilityTol=1e-09,
            OutputFlag=0,
        )
        self.assertGreater(dist, 0.1)
        # print("chebyshev distance is : " + str(dist))

        pre_b_dist = reduced_polytope.border_distance(x)
        self.assertGreater(pre_b_dist, 0.1)
        # print("border distance pre-transformation is: " + str(pre_b_dist))

        # put x at zero!
        reduced_polytope.apply_shift(x)
        # b = b - np.squeeze(np.matmul(A, x))
        x_0 = np.zeros(x.shape)
        b_dist_at_zero = reduced_polytope.border_distance(x_0)
        self.assertGreater(b_dist_at_zero, 0.1)
        self.assertAlmostEqual(pre_b_dist, b_dist_at_zero)
        # print("border distance zero-transformation is: " + str(b_dist_at_zero))

        transformation = PolytopeReducer.null_space(reduced_polytope.S.values, eps=eps)
        reduced_polytope.apply_transformation(transformation)
        # A_null = np.matmul(A, null)
        u = np.zeros((transformation.shape[1], 1))

        norm_check = np.linalg.norm(np.matmul(polytope.S.values, transformation))
        self.assertLess(norm_check, 1e-10)
        # print("norm of the null space is: " + str(norm_check))

        b_dist = reduced_polytope.border_distance(u)
        self.assertAlmostEqual(b_dist, pre_b_dist)

        # test if we can reproduce the original x
        x_rec = reduced_polytope.back_transform(u)

        self.assertLess(np.min(np.abs(x - x_rec)), 1e-10)

        # Do FVA and see if the points are feasible in the original space
        points = ChebyshevFinder.fva(reduced_polytope, backend="glpk")

        # convert all points to original space
        back = reduced_polytope.back_transform(points.values)
        b_dists = polytope.border_distance(back)
        self.assertGreater(b_dists, -1e-9)
        # print("done")

    def test_api_simplification_coli(self):
        polytope = StoichiometryParser.parse_sbml_cobrapy(self.input)
        x, dist = ChebyshevFinder.chebyshev_center(polytope)
        self.assertTrue(np.abs(dist) < 1e-10)
        reduced = PolyRoundApi.simplify_polytope(polytope)
        x, dist = ChebyshevFinder.chebyshev_center(reduced)
        self.assertTrue(np.abs(dist) > 1e-10)
        transformed = PolyRoundApi.transform_polytope(reduced, verbose=True)
        x, dist = ChebyshevFinder.chebyshev_center(transformed)
        self.assertTrue(np.abs(dist) > 1e-10)
        rounded = PolyRoundApi.round_polytope(transformed)
        self.assertTrue(rounded.inequality_only)
        x, dist = ChebyshevFinder.chebyshev_center(rounded)
        self.assertTrue(np.abs(dist) > 1e-10)
        PolyRoundApi.polytope_to_csvs(
            rounded, os.path.join("PolyRound", "output", "export_test")
        )


if __name__ == "__main__":
    unittest.main()
