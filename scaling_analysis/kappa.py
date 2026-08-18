import numpy as np
from scipy import sparse
from scaling import carleman_L

print("Which 'kappa' matches Setty's design choices?\n")
print(f"{'case':>12} {'alpha':>8} {'sig_max':>8} {'sig_min':>8} {'sM/sm':>8} "
      f"{'alpha/sm':>9} {'kappa_paper':>11}")

# Burgers, Setty section 4.3
L, A, D, dx = carleman_L(5, 2, nu=0.01, dt=0.1)
sv = np.linalg.svd(L.toarray(), compute_uv=False)
Lc = L.tocoo(); pairs = set(zip(np.round(Lc.data, 9), Lc.row - Lc.col))
alpha = sum(abs(v) for v, _ in pairs)
print(f"{'Burgers':>12} {alpha:>8.3f} {sv[0]:>8.3f} {sv[-1]:>8.3f} {sv[0]/sv[-1]:>8.3f} "
      f"{alpha/sv[-1]:>9.3f} {8:>11}")

# Heat equation, Setty section 4.2 : eq (D.8) with lambda = 0.64, N=8 interior points (n=3 qubits)
for Ngrid, qb in [(8, 3), (16, 4)]:
    lam = 0.64
    Ah = np.diag((1+2*lam)*np.ones(Ngrid)) + np.diag(-lam*np.ones(Ngrid-1), 1) \
         + np.diag(-lam*np.ones(Ngrid-1), -1)
    Ah[-1, -2] = -2*lam
    svh = np.linalg.svd(Ah, compute_uv=False)
    pr = set()
    for r in range(Ngrid):
        for c in range(Ngrid):
            if abs(Ah[r, c]) > 1e-12: pr.add((round(Ah[r, c], 9), r-c))
    al = sum(abs(v) for v, _ in pr)
    kp = {3: 8, 4: 12}[qb]
    print(f"{'heat n='+str(qb):>12} {al:>8.3f} {svh[0]:>8.3f} {svh[-1]:>8.3f} "
          f"{svh[0]/svh[-1]:>8.3f} {al/svh[-1]:>9.3f} {kp:>11}")

print("\n=> alpha/sigma_min tracks the paper's kappa; sigma_max/sigma_min does not.\n")

# NOTE: measured max row nnz is consistently 4 less than "4N+1" (5 vs 9 at
# N=2, 9 vs 13 at N=3) -- the prediction formula is off by a constant here,
# not extended/re-derived.
print("Row sparsity of L (predicted 4N+1):")
for nx in [5, 7, 9]:
    for N in [2, 3]:
        L, A, D, dx = carleman_L(nx, N, nu=0.01, dt=0.1)
        s = int(np.diff(L.tocsr().indptr).max())
        print(f"  nx={nx} N={N}: max row nnz = {s}  (4N+1 = {4*N+1})")

print("\nGrowth of alpha with (nx, N)  [alpha ~ kappa_QSVT]:")
print(f"{'nx':>4} {'N':>2} {'n_data':>8} {'alpha':>10} {'nx^(N-1)*lcfl':>14}")
for nx in [5, 7, 9, 15, 21]:
    for N in [2, 3]:
        if nx**N > 20000: continue
        L, A, D, dx = carleman_L(nx, N, nu=0.01, dt=0.1)
        Lc = L.tocoo(); pr = set(zip(np.round(Lc.data, 9), Lc.row-Lc.col))
        al = sum(abs(v) for v, _ in pr)
        lcfl = 0.1/dx
        print(f"{nx:>4} {N:>2} {len(pr):>8} {al:>10.2f} {nx**(N-1)*lcfl:>14.2f}")

print("\nSparse-oracle alternative: alpha_sparse = s * ||L||_max")
for nx in [5, 7, 9, 15]:
    for N in [2, 3]:
        if nx**N > 20000: continue
        L, A, D, dx = carleman_L(nx, N, nu=0.01, dt=0.1)
        s = int(np.diff(L.tocsr().indptr).max())
        lmax = abs(L).max()
        Lc = L.tocoo(); pr = set(zip(np.round(Lc.data, 9), Lc.row-Lc.col))
        al = sum(abs(v) for v, _ in pr)
        print(f"  nx={nx} N={N}: alpha_coherent-perm={al:9.2f}   "
              f"alpha_sparse=s*Lmax={s*lmax:7.2f}   ratio={al/(s*lmax):6.2f}")
