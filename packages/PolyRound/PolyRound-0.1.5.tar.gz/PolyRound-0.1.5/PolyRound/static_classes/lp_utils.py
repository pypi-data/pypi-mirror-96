import numpy as np
import pandas as pd
from PolyRound.static_classes.lp_interfacing import OptlangInterfacer


class ChebyshevFinder:
    @staticmethod
    def chebyshev_center(
        polytope, backend="glpk", regularize=False, sgp=False, **kwargs
    ):
        # get norm col
        a_norm = np.linalg.norm(polytope.A.values, axis=1).reshape(
            (polytope.A.shape[0], 1)
        )
        A_ext = np.concatenate((polytope.A.values, a_norm), axis=1)
        obj = np.zeros(A_ext.shape[1])
        obj[-1] = -1
        if polytope.inequality_only:
            x, m = OptlangInterfacer.gurobi_solve(
                obj, A_ext, polytope.b.values, backend, sgp=sgp, **kwargs
            )
        else:
            s_0_col = np.zeros(shape=(polytope.S.shape[0], 1))
            S_ext = np.concatenate((polytope.S.values, s_0_col), axis=1)
            # sol = solvers.lp(matrix(obj), matrix(A_ext), matrix(b_np), A=matrix(S_ext), b=matrix(h), solver='glpk')
            # print(sol)
            x, m = OptlangInterfacer.gurobi_solve(
                obj,
                A_ext,
                polytope.b.values,
                backend,
                S=S_ext,
                h=polytope.h.values,
                sgp=sgp,
                **kwargs
            )
        if regularize:
            x_reg, m = OptlangInterfacer.gurobi_regularize_chebyshev_center(
                x[-1], m, backend
            )
            x = x_reg
        x = x.reshape((x.shape[0], 1))
        return x[:-1], x[-1]

    @staticmethod
    def fva(polytope, backend):
        n_reac = polytope.A.shape[1]
        output = pd.DataFrame(index=polytope.A.columns)
        # make the first run
        obj = np.ones(n_reac)

        if polytope.inequality_only:
            x, m = OptlangInterfacer.gurobi_solve(
                obj, polytope.A.values, polytope.b.values, backend
            )
        else:
            x, m = OptlangInterfacer.gurobi_solve(
                obj,
                polytope.A.values,
                polytope.b.values,
                backend,
                S=polytope.S.values,
                h=polytope.h.values,
            )

        obj = np.zeros(n_reac)
        # Now run all the remaining directions
        for i in range(0, n_reac * 2):
            ind = i // 2
            if i % 2 == 0:
                obj[ind] = 1
            else:
                obj[ind] = -1
            x, m = OptlangInterfacer.gurobi_solve_model(obj, m, backend)
            obj[ind] = 0
            output.loc[:, i] = x
        return output
