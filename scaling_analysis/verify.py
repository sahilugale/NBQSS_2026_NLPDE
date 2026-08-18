import numpy as np
np.set_printoptions(precision=4, suppress=True, linewidth=200)

# ---- Setty section 4.3 parameters ----
S   = 7                 # total grid points
nx  = S - 2             # interior points
dx  = 1.0/(S-1)
nu  = 0.01
dt  = 0.1
T   = 0.3
N   = 2                 # Carleman truncation order
L_  = 1.0               # domain length
U   = 1.0               # amplitude of u0

lam1 = nu/dx**2         # F1 prefactor
lam2 = -1.0/(2*dx)      # F2 prefactor
print(f"nx={nx} dx={dx:.4f} lam1={lam1} lam2={lam2}  Re=U*L/nu={U*L_/nu}")

# ---- F1 : eq (F.3) ----
F1 = lam1*(np.diag(-2*np.ones(nx)) + np.diag(np.ones(nx-1),1) + np.diag(np.ones(nx-1),-1))

# ---- F2 : eq (F.2) nonlinear term  -1/(2dx) * u_i (u_{i+1}-u_{i-1}) ----
# acts on u (x) u ; index (i, i*nx+j)
F2 = np.zeros((nx, nx*nx))
for i in range(nx):
    if i+1 < nx:  F2[i, i*nx + (i+1)] += lam2*( 1.0)
    if i-1 >= 0:  F2[i, i*nx + (i-1)] += lam2*(-1.0)

I  = np.eye(nx)
# ---- Carleman blocks, eqs (E.4),(E.5) ----
A11 = F1
A12 = np.kron(F2, I) + np.kron(I, F2)          # maps R^{nx^3}->R^{nx^2}?? careful
# For j=1: A^1_2 = F2  (only one term)  -> R^{nx^2} -> R^{nx}
A12 = F2
# For j=2: A^2_2 = F1 (x) I + I (x) F1
A22 = np.kron(F1, I) + np.kron(I, F1)

D = nx + nx*nx
A = np.zeros((D, D))
A[:nx, :nx]  = A11
A[:nx, nx:]  = A12
A[nx:, nx:]  = A22
# A^2_1 = 0 because F0 = 0

Lmat = np.eye(D) - dt*A
print(f"\nDim(A) = {D}   (paper: 30)   matrix qubits = {int(np.ceil(np.log2(D)))} (paper: 5)")

# ---- distinct data values of L (block-encoding data vector) ----
vals, counts = np.unique(np.round(Lmat[np.abs(Lmat)>1e-12], 6), return_counts=True)
print("\ndistinct nonzero values of L and multiplicities:")
for v,c in zip(vals, counts): print(f"   {v:+.4f}  x{c}")

# number of (value, diagonal-offset) pairs = number of data elements
pairs = set()
for r in range(D):
    for c in range(D):
        if abs(Lmat[r,c])>1e-12:
            pairs.add((round(Lmat[r,c],6), r-c))
print(f"\n#(value,offset) pairs = {len(pairs)}   (paper: 14 data elements -> 4 data qubits)")
print(f"formula 2N(N+1)+N = {2*N*(N+1)+N}")

# ---- subnormalisation alpha = L1 norm of distinct data values ----
# NOTE: alpha_formula below doesn't match alpha_naive exactly (4.23 vs 4.76
# at this nx, N) -- close but not exact, formula not fully reconciled.
alpha_naive = sum(abs(v) for v,_ in pairs)
print(f"\nalpha (sum |distinct data values|) = {alpha_naive:.4f}")
lam_diff = nu*dt/dx**2
lam_cfl  = dt/dx
alpha_formula = N + 2*N*(N+1)*lam_diff + N*(N+1)*lam_cfl/2
print(f"lam_diff={lam_diff:.4f}  lam_cfl={lam_cfl:.4f}")
print(f"alpha formula  N + 2N(N+1)lam_diff + N(N+1)lam_cfl/2 = {alpha_formula:.4f}")

# ---- spectrum / condition number ----
sv = np.linalg.svd(Lmat, compute_uv=False)
print(f"\nsigma_max(L)={sv[0]:.4f}  sigma_min(L)={sv[-1]:.4f}  kappa(L)={sv[0]/sv[-1]:.4f}")
print(f"kappa of subnormalised L/alpha is identical (scale invariant): {sv[0]/sv[-1]:.4f}")
ev = np.linalg.eigvals(A)
print(f"eig(A): max|Re| = {np.abs(ev.real).max():.4f}, min|Re| = {np.abs(ev.real).min():.4f}")
print(f"predicted |Re lam1(F1)| ~ pi^2 nu/L^2 = {np.pi**2*nu/L_**2:.4f}; exact = {np.abs(np.linalg.eigvals(F1).real).min():.4f}")

# ---- Carleman convergence ratio R (Liu et al. convention) ----
x = np.arange(1, nx+1)*dx
u0 = U*np.sin(2*np.pi*x)
nrm_u0 = np.linalg.norm(u0)
nrm_F2 = np.linalg.norm(F2, 2)
re_lam1 = np.abs(np.linalg.eigvals(F1).real).min()
R = nrm_u0*nrm_F2/re_lam1
print(f"\n||u0||_2={nrm_u0:.4f}  ||F2||_2={nrm_F2:.4f}  |Re lam1|={re_lam1:.4f}")
print(f"R = ||u0|| ||F2|| / |Re lam1| = {R:.3f}    (need R<1 for Liu et al. bound)")
print(f"analytic R ~ Re*nx^1.5/(2 pi^2) = {(U*L_/nu)*nx**1.5/(2*np.pi**2):.3f}")
print(f"physical R* = 2 Re/pi = {2*(U*L_/nu)/np.pi:.3f}")

# ---- Carleman block-1 readout probability ----
g2 = nrm_u0**2
p1 = g2/sum(g2**j for j in range(1, N+1))
print(f"\ngamma^2=||u0||^2={g2:.4f};  P(block 1) = {p1:.4f}")
for NN in [2,3,4,6,8]:
    print(f"   N={NN}: P(block1) = {g2/sum(g2**j for j in range(1,NN+1)):.5f}")

# ---- success probability model ----
b = np.zeros(D); b[:nx] = u0/np.linalg.norm(u0)
Lb = np.linalg.solve(Lmat.conj().T/alpha_naive, b)
kappa_eff = np.linalg.norm(Lb)
for kappa_design in [8]:
    ps = (kappa_eff/(2*kappa_design))**2
    print(f"\nkappa_eff=||(L^dag/alpha)^-1 |b>||={kappa_eff:.4f}; with kappa_design={kappa_design}: ps={ps:.5f} (paper 0.0865)")

# ---- depth model calibration from paper tables ----
print("\n--- depth model calibration (heavy-hex) ---")
data = [("tridiag",117,283,57e3,3,3),("heat n=3",559,311,258e3,3,2),
        ("heat n=4",1275,550,903e3,4,2),("Burgers",559,5687,3.4e6,5,4)]
for name,d,BE,QS,qM,mdat in data:
    Dpi = QS/d - BE
    print(f"{name:10s} d={d:5d} BE={BE:6.0f} QSVT={QS:9.3g}  =>  D_Pi={Dpi:7.1f}  (qM={qM}, m_data={mdat})")
    print(f"           BE/(n_data*qM^2) with n_data=2^m_data: {BE/((2**mdat)*qM**2):.2f}")
