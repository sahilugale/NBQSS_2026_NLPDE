import numpy as np
from scipy import sparse
from scipy.sparse.linalg import svds, norm as spnorm

def carleman_L(nx, N, nu, dt, Lspan=1.0):
    """Build L = I - dt*A for Carleman-linearised Burgers, Setty eqs (E.3)-(E.5),(F.3),(F.4)."""
    dx = Lspan/(nx+1)
    lam1 = nu/dx**2
    lam2 = -1.0/(2*dx)
    F1 = sparse.diags([lam1*np.ones(nx-1), -2*lam1*np.ones(nx), lam1*np.ones(nx-1)],
                      [-1, 0, 1], format='csr')
    rows, cols, vals = [], [], []
    for i in range(nx):
        if i+1 < nx: rows.append(i); cols.append(i*nx + (i+1)); vals.append( lam2)
        if i-1 >= 0: rows.append(i); cols.append(i*nx + (i-1)); vals.append(-lam2)
    F2 = sparse.csr_matrix((vals, (rows, cols)), shape=(nx, nx*nx))

    dims = [nx**j for j in range(1, N+1)]
    offs = np.cumsum([0]+dims)
    D = offs[-1]
    A = sparse.lil_matrix((D, D))
    for j in range(1, N+1):
        # A^j_j = sum_v I^{ox v} (x) F1 (x) I^{ox j-1-v}
        Ajj = sparse.csr_matrix((nx**j, nx**j))
        for v in range(j):
            Ajj = Ajj + sparse.kron(sparse.kron(sparse.eye(nx**v), F1), sparse.eye(nx**(j-1-v)))
        A[offs[j-1]:offs[j], offs[j-1]:offs[j]] = Ajj
        if j < N:
            Ajj1 = sparse.csr_matrix((nx**j, nx**(j+1)))
            for v in range(j):
                Ajj1 = Ajj1 + sparse.kron(sparse.kron(sparse.eye(nx**v), F2), sparse.eye(nx**(j-1-v)))
            A[offs[j-1]:offs[j], offs[j]:offs[j+1]] = Ajj1
    A = A.tocsr()
    L = sparse.eye(D, format='csr') - dt*A
    return L, A, D, dx

def _main():
    print(f"{'nx':>4} {'N':>2} {'Dim':>10} {'qM':>4} {'n_data':>7} {'m_dat':>6} {'alpha':>9} "
          f"{'kap(L)':>8} {'2N':>4} {'2nx-2':>6}")
    for nx in [5, 7, 9, 15]:
        for N in [2, 3]:
            if nx**N > 20000: continue
            L, A, D, dx = carleman_L(nx, N, nu=0.01, dt=0.1)
            Lc = L.tocoo()
            pairs = set(zip(np.round(Lc.data, 9), Lc.row - Lc.col))
            n_data = len(pairs)
            alpha = sum(abs(v) for v, _ in pairs)
            Ld = L.toarray()
            sv = np.linalg.svd(Ld, compute_uv=False)
            kap = sv[0]/sv[-1]
            print(f"{nx:>4} {N:>2} {D:>10} {int(np.ceil(np.log2(D))):>4} {n_data:>7} "
                  f"{int(np.ceil(np.log2(n_data))):>6} {alpha:>9.3f} {kap:>8.3f} {2*N:>4} {2*nx-2:>6}")

    # NOTE: this F2-offset prediction only matches the measured count at N=2
    # (e.g. nx=5: pred 24 vs measured 56 at N=3) -- the combinatorics get
    # more complex beyond N=2 and the formula wasn't extended. Treat the
    # printed "pred" values at N=3 as wrong, not as a confirmed result.
    print("\n--- decompose n_data into F1-part and F2-part ---")
    for nx in [5, 7, 9]:
        for N in [2, 3]:
            if nx**N > 20000: continue
            L, A, D, dx = carleman_L(nx, N, nu=0.01, dt=0.1)
            Lc = L.tocoo()
            lam1 = 0.01/dx**2; lam2 = -1.0/(2*dx)
            f1pairs = set(); f2pairs = set(); diagpairs = set()
            for v, r, c in zip(np.round(Lc.data, 9), Lc.row, Lc.col):
                if r == c:                       diagpairs.add((v, 0))
                elif abs(abs(v) - 0.1*lam1) < 1e-9: f1pairs.add((v, r-c))
                else:                            f2pairs.add((v, r-c))
            print(f"nx={nx} N={N}: diag={len(diagpairs)} (pred {N}), "
                  f"F1-offsets={len(f1pairs)} (pred {2*N}), "
                  f"F2-offsets={len(f2pairs)} (pred 2(nx-1)*sum_j j = {2*(nx-1)*sum(range(1,N))})")

    print("\n--- kappa(L) vs dt at fixed nx (fixed-dt policy) ---")
    nx, N = 7, 2
    for dt in [0.01, 0.05, 0.1, 0.5, 1.0, 4.0]:
        L, A, D, dx = carleman_L(nx, N, nu=0.01, dt=dt)
        sv = np.linalg.svd(L.toarray(), compute_uv=False)
        Lc = L.tocoo(); pairs = set(zip(np.round(Lc.data, 9), Lc.row-Lc.col))
        alpha = sum(abs(v) for v, _ in pairs)
        ldiff = 0.01*dt/dx**2; lcfl = dt/dx
        pred = N + N*(N+1)*ldiff + 2*N*ldiff + 2*(nx-1)*sum(range(1, N))*lcfl/2
        print(f"dt={dt:5.2f} lam_diff={ldiff:7.4f} lam_cfl={lcfl:6.3f} "
              f"alpha={alpha:8.3f} (pred {pred:8.3f}) kappa(L)={sv[0]/sv[-1]:7.3f}")


if __name__ == "__main__":
    _main()
