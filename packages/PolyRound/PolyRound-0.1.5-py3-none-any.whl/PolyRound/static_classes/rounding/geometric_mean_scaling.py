import numpy as np


def geometric_mean_scaling(A, iprint, scltol):
    if iprint > 0:
        print("gmscale: Geometric-Mean scaling of matrix")
        print("ax col ratio")

    [m, n] = A.shape
    A = np.abs(A)
    maxpass = 150
    aratio = 1e50
    damp = 1e-4
    rscale = np.ones((m, 1))
    cscale = np.ones((n, 1))

    for npass in range(maxpass + 1):

        # Find the largest column ratio.
        # Also set new column scales (except on pass 0).

        rscale[rscale == 0] = 1
        # Rinv    = diag(sparse(1./rscale));
        SA = np.multiply(A.transpose(), 1 / rscale.squeeze()).transpose()  # Rinv*A
        # [I,J,V] = find(SA);
        with np.errstate(divide="ignore"):
            invSA = 1 / SA  # sparse(I,J,1./V,m,n);
        cmax = np.max(SA, axis=0).transpose()  # full(max(   SA))';   % column vector
        cmin = np.max(invSA, axis=0)  # full(max(invSA))';   % column vector
        cmin = 1.0 / (cmin + np.spacing(1))
        with np.errstate(divide="ignore"):
            sratio = np.max(cmax / cmin)
        if npass > 0:
            cscale = np.sqrt(np.maximum(cmin, damp * cmax) * cmax)

        if iprint > 0:
            print(npass, sratio)

        if npass >= 2 and sratio >= aratio * scltol:
            break
        if npass == maxpass:
            break
        aratio = sratio

        # Set new row scales for the next pass.

        cscale[cscale == 0] = 1
        # Cinv    = diag(sparse(1./cscale));
        SA = np.multiply(A, 1 / cscale.squeeze())  # A*Cinv;                  % Scaled A
        # [I,J,V] = find(SA);
        with np.errstate(divide="ignore"):
            invSA = 1 / SA  # sparse(I,J,1./V,m,n);
        rmax = np.max(SA, axis=1).transpose()  # full(max(   SA))';   % column vector
        rmin = np.max(invSA, axis=1)  # full(max(invSA))';   % column vector
        rmin = 1.0 / (rmin + np.spacing(1))
        rscale = np.sqrt(np.maximum(rmin, damp * rmax) * rmax)

    # Reset column scales so the biggest element
    # in each scaled column will be 1.
    # Again, allow for empty rows and columns.

    rscale[rscale == 0] = 1
    # Rinv = diag(sparse(1. / rscale));
    SA = np.multiply(A.transpose(), 1 / rscale).transpose()
    # [I, J, V] = find(SA);
    cscale = np.max(SA, axis=0).transpose()
    cscale[cscale == 0] = 1

    return cscale, rscale
