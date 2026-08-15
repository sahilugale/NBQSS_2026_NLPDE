import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import sys
sys.path.insert(0, '/home/claude')
import scaling
from scaling import carleman_L

plt.rcParams.update({'font.size': 9, 'axes.grid': True, 'grid.alpha': 0.3,
                     'figure.dpi': 200, 'savefig.bbox': 'tight',
                     'font.family': 'serif', 'mathtext.fontset': 'dejavuserif'})

# ---------------- Fig 1 : Carleman order N required vs Reynolds number ----------
fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.7))
Re = np.linspace(0.01, 1.55, 500)
Rstar = 2*Re/np.pi
for eps, ls in [(1e-2, '-'), (1e-3, '--'), (1e-4, ':')]:
    Nreq = np.log(1/eps)/np.log(1/Rstar)
    ax[0].plot(Re, Nreq, ls, color='k', lw=1.3, label=rf'$\epsilon={eps:g}$')
ax[0].axvline(np.pi/2, color='crimson', lw=1.2)
ax[0].text(np.pi/2-0.03, 40, r'$\mathrm{Re}=\pi/2$', rotation=90,
           ha='right', va='center', color='crimson', fontsize=8)
ax[0].set_yscale('log'); ax[0].set_ylim(1, 300); ax[0].set_xlim(0, 1.7)
ax[0].set_xlabel(r'Reynolds number $\mathrm{Re}=UL/\nu$')
ax[0].set_ylabel(r'required Carleman order $N$')
ax[0].legend(frameon=False, fontsize=8, loc='upper left')
ax[0].set_title(r'(a) $N=\lceil\ln(1/\epsilon)/\ln(1/R_\star)\rceil$', fontsize=9)

# Carleman block-1 readout probability
gam2 = np.array([0.5, 1.5, 3.0])
Ns = np.arange(1, 13)
for g2, mk in zip(gam2, ['o', 's', '^']):
    if g2 < 1:
        p1 = (1-g2)/(1-g2**Ns)
    else:
        p1 = np.array([g2/sum(g2**j for j in range(1, n+1)) for n in Ns])
    ax[1].semilogy(Ns, p1, mk+'-', color='k', ms=3, lw=1.0,
                   mfc='none', label=rf'$\gamma^2={g2:g}$')
ax[1].set_xlabel(r'Carleman order $N$')
ax[1].set_ylabel(r'$P_1$  (block-1 post-selection)')
ax[1].legend(frameon=False, fontsize=8)
ax[1].set_title(r'(b) cost of reading $\hat{u}$ out of $\hat{y}$', fontsize=9)
plt.savefig('/home/claude/fig_carleman.pdf')
plt.close()

# ---------------- Fig 2 : subnormalisation alpha, two block-encoding routes -----
nxs = [5, 7, 9, 11, 15, 21, 27]
a_cp, a_sp, nd_cp, kap = [], [], [], []
for nx in nxs:
    L, A, D, dx = carleman_L(nx, 2, nu=0.01, dt=0.1)
    Lc = L.tocoo()
    pr = set(zip(np.round(Lc.data, 9), Lc.row - Lc.col))
    a_cp.append(sum(abs(v) for v, _ in pr)); nd_cp.append(len(pr))
    s = int(np.diff(L.tocsr().indptr).max())
    a_sp.append(s*abs(L).max())
    sv = np.linalg.svd(L.toarray(), compute_uv=False)
    kap.append(sv[-1])

fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.7))
ax[0].loglog(nxs, a_cp, 'ko-', ms=3.5, lw=1.1, mfc='none',
             label=r'coherent permutation, $\alpha_{\rm cp}$')
ax[0].loglog(nxs, a_sp, 'ks--', ms=3.5, lw=1.1,
             label=r'sparse arithmetic oracle, $\alpha_{\rm sp}$')
ref = np.array(nxs, float); ref = a_cp[0]*(ref/ref[0])**2
ax[0].loglog(nxs, ref, 'k:', lw=0.9, label=r'$\propto n_x^2$')
ax[0].set_xlabel(r'interior grid points $n_x$')
ax[0].set_ylabel(r'subnormalisation $\alpha$')
ax[0].legend(frameon=False, fontsize=7.5, loc='upper left')
ax[0].set_title(r'(a) $N=2$, $\nu=0.01$, $\Delta t=0.1$', fontsize=9)

Ns2 = [2, 3]
for nx, mk in zip([5, 7, 9], ['o', 's', '^']):
    ac, asp = [], []
    for N in Ns2:
        L, A, D, dx = carleman_L(nx, N, nu=0.01, dt=0.1)
        Lc = L.tocoo(); pr = set(zip(np.round(Lc.data, 9), Lc.row-Lc.col))
        ac.append(sum(abs(v) for v, _ in pr))
        s = int(np.diff(L.tocsr().indptr).max()); asp.append(s*abs(L).max())
    ax[1].semilogy(Ns2, ac, mk+'-', color='k', ms=3.5, lw=1.1, mfc='none',
                   label=rf'$n_x={nx}$, cp')
    ax[1].semilogy(Ns2, asp, mk+'--', color='0.55', ms=3.5, lw=1.1,
                   label=rf'$n_x={nx}$, sp')
ax[1].set_xlabel(r'Carleman order $N$'); ax[1].set_xticks([2, 3])
ax[1].set_ylabel(r'subnormalisation $\alpha$')
ax[1].legend(frameon=False, fontsize=7, ncol=2)
ax[1].set_title(r'(b) growth with $N$', fontsize=9)
plt.savefig('/home/claude/fig_alpha.pdf')
plt.close()

# ---------------- Fig 3 : depth model calibration -----------------------------
cases = [('tridiag', 117, 283, 57e3, 3, 6, 4),
         ('heat $n{=}3$', 559, 311, 258e3, 3, 4, 3),
         ('heat $n{=}4$', 1275, 550, 903e3, 4, 4, 3),
         ('Burgers', 559, 5687, 3.4e6, 5, 14, 5)]
pred, meas, labs = [], [], []
for nm, d, BE, QS, qM, ndat, mfl in cases:
    pred.append(d*(10*ndat*qM**2 + 15*mfl**2)); meas.append(QS); labs.append(nm)

fig, ax = plt.subplots(figsize=(3.4, 3.0))
ax.loglog([2e4, 6e6], [2e4, 6e6], 'k-', lw=0.8)
ax.loglog([2e4, 6e6], [4e4, 1.2e7], 'k:', lw=0.7)
ax.loglog([2e4, 6e6], [1e4, 3e6], 'k:', lw=0.7)
ax.loglog(pred, meas, 'ko', ms=5, mfc='none')
for p, m, l in zip(pred, meas, labs):
    ax.annotate(l, (p, m), textcoords='offset points', xytext=(6, -8), fontsize=7)
ax.set_xlabel(r'model  $d\,(c_{\rm BE}n_{\rm data}q_M^2+c_\Pi m_{\rm flag}^2)$')
ax.set_ylabel(r'reported two-qubit depth (heavy-hex)')
ax.set_title(r'$c_{\rm BE}=10,\ c_\Pi=15$; dotted: factor 2', fontsize=8)
plt.savefig('/home/claude/fig_depth.pdf')
plt.close()
print("figures written")