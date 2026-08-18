"""Variational PDE time-stepper via natural-gradient descent.

Each timestep minimizes ||amp*psi(theta) - target_u||^2, target_u = u_id +
dt*(F1 u_rhs + F2 kron(u_rhs, u_rhs)) -- theta_rhs/amp_rhs default to
theta_id/amp_id (forward Euler); KdV passes a separately-solved implicit-
midpoint state instead (see natural_gradient_timestep, target_C0).

Every quantity (metric M_kl, cross terms) is measured via compute-uncompute
circuits + P(all-zero)/<X>, no full-ansatz controlled doubling. Signs
(P(all-zero) only gives magnitude) are resolved by SignTracker: carried
forward for free when a proven Lipschitz bound rules out a zero-crossing,
else one classical O(2^n) check per term.
"""

import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import real_amplitudes
from qiskit.quantum_info import Statevector, Operator, SparsePauliOp

# |C0| below which F=C0^2's derivative formula F'/(4*C0) is 0/0 (not just
# ill-conditioned); falls back to a classical finite difference instead.
EPSILON_CROSS = 1e-6


def build_ansatz_template(n, reps=None):
    return real_amplitudes(n, reps=(reps if reps is not None else n), entanglement="linear")


def shift_gate(n):
    """Ancilla-free cyclic increment |m> -> |m+1 mod 2**n>."""
    qc = QuantumCircuit(n)
    for i in range(n - 1, 0, -1):
        qc.mcx(list(range(i)), i)
    qc.x(0)
    return qc


def shift_power(n, power, inverse):
    base = shift_gate(n).inverse() if inverse else shift_gate(n)
    qc = QuantumCircuit(n)
    for _ in range(power):
        qc = qc.compose(base)
    return qc


def _ry_positions(bound):
    return [i for i, instr in enumerate(bound.data) if instr.operation.name == "ry"]


def _subcircuit(bound, n, lo, hi):
    qc = QuantumCircuit(n)
    for instr in bound.data[lo:hi]:
        qc.append(instr.operation, instr.qubits, instr.clbits)
    return qc


def psi_of(ansatz_template, theta):
    return np.real(Statevector(ansatz_template.assign_parameters(theta)).data)


def metric_offdiag_circuit(ansatz_template, theta, k, l):
    """Single-ancilla, two-generator-insertion circuit for M_kl (k<l)."""
    n = ansatz_template.num_qubits
    bound = ansatz_template.assign_parameters(theta)
    ry_pos = _ry_positions(bound)
    idx_k, idx_l = ry_pos[k], ry_pos[l]
    U_before_k = _subcircuit(bound, n, 0, idx_k)
    tq_k = bound.find_bit(bound.data[idx_k].qubits[0]).index
    U_mid = _subcircuit(bound, n, idx_k + 1, idx_l)
    tq_l = bound.find_bit(bound.data[idx_l].qubits[0]).index
    U_after_l = _subcircuit(bound, n, idx_l + 1, len(bound.data))

    anc = 0
    sys_q = list(range(1, n + 1))
    qc = QuantumCircuit(1 + n)
    qc.append(U_before_k.to_gate(), sys_q)
    qc.ry(theta[k], sys_q[tq_k])
    qc.h(anc)
    qc.x(anc)
    qc.cy(anc, sys_q[tq_k])
    qc.x(anc)
    qc.append(U_mid.to_gate(), sys_q)
    qc.ry(theta[l], sys_q[tq_l])
    qc.cy(anc, sys_q[tq_l])
    qc.append(U_after_l.to_gate(), sys_q)
    return qc


def measure_metric_offdiag(ansatz_template, theta, k, l):
    n = ansatz_template.num_qubits
    qc = metric_offdiag_circuit(ansatz_template, theta, k, l)
    X_op = SparsePauliOp("I" * n + "X")
    return 0.25 * Statevector(qc).expectation_value(X_op).real


def full_metric(ansatz_template, theta):
    """M_kk = 1/4 always (Pauli-generator rotation, no circuit needed)."""
    P = len(theta)
    M = np.eye(P) * 0.25
    for k in range(P):
        for l in range(k + 1, P):
            M[k, l] = M[l, k] = measure_metric_offdiag(ansatz_template, theta, k, l)
    return M


def nonlinear_overlap_circuit(ansatz_template, theta, alpha, shift_B_qc, shift_A_qc=None):
    """P(all-zero) = <psi(alpha)|chi(theta)>^2, chi_i=(S_A psi)_i*(S_B psi)_i.
    shift_A_qc=None: chi_i=psi_i*(S_B psi)_i (skew F2's cross term);
    shift_A_qc=shift_B_qc: chi_i=(S_B psi)_i^2 (its square term)."""
    n = ansatz_template.num_qubits
    A_q = list(range(n))
    B_q = list(range(n, 2 * n))
    qc = QuantumCircuit(2 * n)
    qc.append(ansatz_template.assign_parameters(theta).to_gate(), A_q)
    qc.append(ansatz_template.assign_parameters(theta).to_gate(), B_q)
    if shift_A_qc is not None:
        qc.append(shift_A_qc.to_gate(), A_q)
    qc.append(shift_B_qc.to_gate(), B_q)
    for j in range(n):
        qc.cx(A_q[j], B_q[j])
    qc.append(ansatz_template.assign_parameters(alpha).inverse().to_gate(), A_q)
    return qc


def measure_all_zero_prob(qc):
    n = qc.num_qubits
    probs = Statevector(qc).probabilities_dict()
    return probs.get("0" * n, 0.0)


def _identity_F(ansatz_template, theta_ref, alpha, extra_shift_qc=None):
    n = ansatz_template.num_qubits
    qc = QuantumCircuit(n)
    qc.append(ansatz_template.assign_parameters(theta_ref).to_gate(), range(n))
    if extra_shift_qc is not None:
        qc.append(extra_shift_qc.to_gate(), range(n))
    qc.append(ansatz_template.assign_parameters(alpha).inverse().to_gate(), range(n))
    return measure_all_zero_prob(qc)


def _operator_real(qc):
    return np.real(Operator(qc).data)


def _classical_id_value(ansatz_template, theta_ref, alpha, extra_shift_qc=None):
    """Exact <psi(alpha)|Op|psi(theta_ref)>, O(2^n) -- fallback only."""
    psi_ref = psi_of(ansatz_template, theta_ref)
    psi_alpha = psi_of(ansatz_template, alpha)
    if extra_shift_qc is not None:
        psi_ref = _operator_real(extra_shift_qc) @ psi_ref
    return np.dot(psi_alpha, psi_ref)


def _classical_nonlinear_value(ansatz_template, theta_chi, alpha, shift_qc, shift_A_qc=None):
    psi_chi = psi_of(ansatz_template, theta_chi)
    S_B = _operator_real(shift_qc) @ psi_chi
    S_A = _operator_real(shift_A_qc) @ psi_chi if shift_A_qc is not None else psi_chi
    chi = S_A * S_B
    psi_alpha = psi_of(ansatz_template, alpha)
    return np.dot(psi_alpha, chi)


def cross_C0(ansatz_template, theta_ref, alpha, sign_hint, extra_shift_qc=None, F0=None):
    if F0 is None:
        F0 = _identity_F(ansatz_template, theta_ref, alpha, extra_shift_qc)
    return sign_hint * np.sqrt(max(F0, 0.0))


def cross_deriv(ansatz_template, theta_ref, alpha, l, sign_hint, extra_shift_qc=None, shift=np.pi / 2, F0=None):
    C0 = cross_C0(ansatz_template, theta_ref, alpha, sign_hint, extra_shift_qc, F0=F0)
    if abs(C0) < EPSILON_CROSS:
        eps = 1e-6
        ap = alpha.copy(); ap[l] += eps
        am = alpha.copy(); am[l] -= eps
        vp = _classical_id_value(ansatz_template, theta_ref, ap, extra_shift_qc)
        vm = _classical_id_value(ansatz_template, theta_ref, am, extra_shift_qc)
        return (vp - vm) / (2 * eps)
    ap = alpha.copy(); ap[l] += shift
    am = alpha.copy(); am[l] -= shift
    Fp = _identity_F(ansatz_template, theta_ref, ap, extra_shift_qc)
    Fm = _identity_F(ansatz_template, theta_ref, am, extra_shift_qc)
    return (Fp - Fm) / (4 * C0)


def nonlinear_cross_C0(ansatz_template, theta_chi, alpha, sign_hint, shift_qc, shift_A_qc=None, F0=None):
    if F0 is None:
        F0 = measure_all_zero_prob(nonlinear_overlap_circuit(ansatz_template, theta_chi, alpha, shift_qc, shift_A_qc))
    return sign_hint * np.sqrt(max(F0, 0.0))


def nonlinear_cross_deriv(ansatz_template, theta_chi, alpha, l, sign_hint, shift_qc, shift_A_qc=None, shift=np.pi / 2, F0=None):
    C0 = nonlinear_cross_C0(ansatz_template, theta_chi, alpha, sign_hint, shift_qc, shift_A_qc=shift_A_qc, F0=F0)
    if abs(C0) < EPSILON_CROSS:
        eps = 1e-6
        ap = alpha.copy(); ap[l] += eps
        am = alpha.copy(); am[l] -= eps
        vp = _classical_nonlinear_value(ansatz_template, theta_chi, ap, shift_qc, shift_A_qc)
        vm = _classical_nonlinear_value(ansatz_template, theta_chi, am, shift_qc, shift_A_qc)
        return (vp - vm) / (2 * eps)
    ap = alpha.copy(); ap[l] += shift
    am = alpha.copy(); am[l] -= shift
    Fp = measure_all_zero_prob(nonlinear_overlap_circuit(ansatz_template, theta_chi, ap, shift_qc, shift_A_qc))
    Fm = measure_all_zero_prob(nonlinear_overlap_circuit(ansatz_template, theta_chi, am, shift_qc, shift_A_qc))
    return (Fp - Fm) / (4 * C0)


# g(alpha_l) = A*cos(alpha_l/2) + B*sin(alpha_l/2) exactly for one Ry
# parameter, so |dg/dalpha_l| <= 1/2 for every term (unit-norm shifts;
# Cauchy-Schwarz for the nonlinear chi/sq vectors).
_DERIV_BOUND = 0.5


def _classical_sign_for_term(name, ansatz_template, theta_id, theta_rhs, alpha, lin_terms, shift_fwd, shift_bwd):
    """O(2^n) sign for one term; theta_id for "id", theta_rhs for the rest."""
    if name == "id":
        return np.sign(_classical_id_value(ansatz_template, theta_id, alpha)) or 1.0
    for lname, Sqc, Sm, coef in lin_terms:
        if name == lname:
            return np.sign(_classical_id_value(ansatz_template, theta_rhs, alpha, Sqc)) or 1.0
    if name == "nl_fwd":
        return np.sign(_classical_nonlinear_value(ansatz_template, theta_rhs, alpha, shift_fwd)) or 1.0
    if name == "nl_bwd":
        return np.sign(_classical_nonlinear_value(ansatz_template, theta_rhs, alpha, shift_bwd)) or 1.0
    if name == "sq_fwd":
        return np.sign(_classical_nonlinear_value(ansatz_template, theta_rhs, alpha, shift_fwd, shift_fwd)) or 1.0
    if name == "sq_bwd":
        return np.sign(_classical_nonlinear_value(ansatz_template, theta_rhs, alpha, shift_bwd, shift_bwd)) or 1.0
    raise ValueError(f"unknown term {name!r}")


class SignTracker:
    """Carries each term's sign forward for free whenever
    |g(last resolved point)| > _DERIV_BOUND * ||new - last||_1 -- which
    provably rules out a zero-crossing on the path between them. Falls
    back to one classical O(2^n) check per term only when that fails."""

    def __init__(self, ansatz_template, theta_id, theta_rhs, lin_terms, shift_fwd, shift_bwd, theta_init, F0s_init):
        self.ansatz_template = ansatz_template
        self.theta_id = theta_id
        self.theta_rhs = theta_rhs
        self.lin_terms = lin_terms
        self.shift_fwd = shift_fwd
        self.shift_bwd = shift_bwd
        self.classical_calls = 0
        self._state = {}  # name -> (theta_point, sign, magnitude)
        for name, F0 in F0s_init.items():
            sign = _classical_sign_for_term(name, ansatz_template, theta_id, theta_rhs, theta_init, lin_terms, shift_fwd, shift_bwd)
            self.classical_calls += 1
            self._state[name] = (theta_init.copy(), sign, np.sqrt(max(F0, 0.0)))

    def signs_at(self, new_theta, F0s):
        signs = {}
        for name, F0 in F0s.items():
            theta_prev, sign_prev, mag_prev = self._state[name]
            delta_l1 = np.sum(np.abs(new_theta - theta_prev))
            if mag_prev > _DERIV_BOUND * delta_l1:
                sign = sign_prev
            else:
                sign = _classical_sign_for_term(name, self.ansatz_template, self.theta_id, self.theta_rhs, new_theta, self.lin_terms, self.shift_fwd, self.shift_bwd)
                self.classical_calls += 1
            signs[name] = sign
            self._state[name] = (new_theta.copy(), sign, np.sqrt(max(F0, 0.0)))
        return signs


def _all_F0s(ansatz_template, theta_id, theta_rhs, theta_trial, lin_terms, shift_fwd, shift_bwd):
    """Shared across all P calls to target_deriv_l (F0 doesn't depend on l)."""
    F0s = {"id": _identity_F(ansatz_template, theta_id, theta_trial)}
    for name, Sqc, Sm, coef in lin_terms:
        F0s[name] = _identity_F(ansatz_template, theta_rhs, theta_trial, Sqc)
    F0s["nl_fwd"] = measure_all_zero_prob(nonlinear_overlap_circuit(ansatz_template, theta_rhs, theta_trial, shift_fwd))
    F0s["nl_bwd"] = measure_all_zero_prob(nonlinear_overlap_circuit(ansatz_template, theta_rhs, theta_trial, shift_bwd))
    F0s["sq_fwd"] = measure_all_zero_prob(nonlinear_overlap_circuit(ansatz_template, theta_rhs, theta_trial, shift_fwd, shift_fwd))
    F0s["sq_bwd"] = measure_all_zero_prob(nonlinear_overlap_circuit(ansatz_template, theta_rhs, theta_trial, shift_bwd, shift_bwd))
    return F0s


def _nl_coef(ansatz_template):
    # F2@kron(psi,psi) = (nl_coef/3)*(chi_fwd-chi_bwd+sq_fwd-sq_bwd);
    # nl_coef = -1/(2dx) = -(2**(n-1)) for dx=1/2**n.
    return -(2 ** (ansatz_template.num_qubits - 1))


def target_C0(ansatz_template, theta_id, theta_rhs, theta_trial, amp_id, amp_rhs, dt, lin_terms, shift_fwd, shift_bwd, signs, F0s=None):
    """<psi(theta_trial) | u_id + dt*(F1 u_rhs + F2(u_rhs kron u_rhs)) >."""
    if F0s is None:
        F0s = _all_F0s(ansatz_template, theta_id, theta_rhs, theta_trial, lin_terms, shift_fwd, shift_bwd)
    c_id = cross_C0(ansatz_template, theta_id, theta_trial, signs["id"], F0=F0s["id"])
    lin = sum(coef * cross_C0(ansatz_template, theta_rhs, theta_trial, signs[name], Sqc, F0=F0s[name]) for name, Sqc, Sm, coef in lin_terms)
    nl_fwd = nonlinear_cross_C0(ansatz_template, theta_rhs, theta_trial, signs["nl_fwd"], shift_fwd, F0=F0s["nl_fwd"])
    nl_bwd = nonlinear_cross_C0(ansatz_template, theta_rhs, theta_trial, signs["nl_bwd"], shift_bwd, F0=F0s["nl_bwd"])
    sq_fwd = nonlinear_cross_C0(ansatz_template, theta_rhs, theta_trial, signs["sq_fwd"], shift_fwd, shift_A_qc=shift_fwd, F0=F0s["sq_fwd"])
    sq_bwd = nonlinear_cross_C0(ansatz_template, theta_rhs, theta_trial, signs["sq_bwd"], shift_bwd, shift_A_qc=shift_bwd, F0=F0s["sq_bwd"])
    nl = (_nl_coef(ansatz_template) / 3.0) * (nl_fwd - nl_bwd + sq_fwd - sq_bwd)
    return amp_id * c_id + dt * amp_rhs * lin + dt * (amp_rhs ** 2) * nl


def target_deriv_l(ansatz_template, theta_id, theta_rhs, theta_trial, l, amp_id, amp_rhs, dt, lin_terms, shift_fwd, shift_bwd, signs, F0s=None):
    if F0s is None:
        F0s = _all_F0s(ansatz_template, theta_id, theta_rhs, theta_trial, lin_terms, shift_fwd, shift_bwd)
    c_id = cross_deriv(ansatz_template, theta_id, theta_trial, l, signs["id"], F0=F0s["id"])
    lin = sum(coef * cross_deriv(ansatz_template, theta_rhs, theta_trial, l, signs[name], Sqc, F0=F0s[name]) for name, Sqc, Sm, coef in lin_terms)
    nl_fwd = nonlinear_cross_deriv(ansatz_template, theta_rhs, theta_trial, l, signs["nl_fwd"], shift_fwd, F0=F0s["nl_fwd"])
    nl_bwd = nonlinear_cross_deriv(ansatz_template, theta_rhs, theta_trial, l, signs["nl_bwd"], shift_bwd, F0=F0s["nl_bwd"])
    sq_fwd = nonlinear_cross_deriv(ansatz_template, theta_rhs, theta_trial, l, signs["sq_fwd"], shift_fwd, shift_A_qc=shift_fwd, F0=F0s["sq_fwd"])
    sq_bwd = nonlinear_cross_deriv(ansatz_template, theta_rhs, theta_trial, l, signs["sq_bwd"], shift_bwd, shift_A_qc=shift_bwd, F0=F0s["sq_bwd"])
    nl = (_nl_coef(ansatz_template) / 3.0) * (nl_fwd - nl_bwd + sq_fwd - sq_bwd)
    return amp_id * c_id + dt * amp_rhs * lin + dt * (amp_rhs ** 2) * nl


def natural_gradient_timestep(ansatz_template, theta_old, amp_old, dt, lin_terms, shift_fwd, shift_bwd, n_iter=60, theta_rhs=None, amp_rhs=None):
    """One timestep: minimize ||amp*psi(theta)-target_u||^2 via natural-
    gradient descent with backtracking line search. theta_rhs/amp_rhs
    default to theta_old/amp_old (forward Euler); pass a separately-solved
    state (e.g. implicit-midpoint u_mid) to fit a different target."""
    if theta_rhs is None:
        theta_rhs = theta_old
    if amp_rhs is None:
        amp_rhs = amp_old
    P = len(theta_old)
    # tiny perturbation: some cross terms vanish exactly at theta_trial=theta_old
    theta_trial = theta_old + np.random.default_rng(0).normal(scale=1e-3, size=P)
    F0s = _all_F0s(ansatz_template, theta_old, theta_rhs, theta_trial, lin_terms, shift_fwd, shift_bwd)
    tracker = SignTracker(ansatz_template, theta_old, theta_rhs, lin_terms, shift_fwd, shift_bwd, theta_trial, F0s)
    signs = tracker.signs_at(theta_trial, F0s)
    cost_prev = -target_C0(ansatz_template, theta_old, theta_rhs, theta_trial, amp_old, amp_rhs, dt, lin_terms, shift_fwd, shift_bwd, signs, F0s=F0s) ** 2
    lr = 1.0
    for _ in range(n_iter):
        F0s = _all_F0s(ansatz_template, theta_old, theta_rhs, theta_trial, lin_terms, shift_fwd, shift_bwd)
        signs = tracker.signs_at(theta_trial, F0s)
        amp_trial = target_C0(ansatz_template, theta_old, theta_rhs, theta_trial, amp_old, amp_rhs, dt, lin_terms, shift_fwd, shift_bwd, signs, F0s=F0s)
        grad = np.array([-2 * amp_trial * target_deriv_l(ansatz_template, theta_old, theta_rhs, theta_trial, l, amp_old, amp_rhs, dt, lin_terms, shift_fwd, shift_bwd, signs, F0s=F0s) for l in range(P)])
        M = full_metric(ansatz_template, theta_trial)
        step = np.linalg.pinv(M, rcond=1e-6) @ grad
        trial_lr = lr
        found = False
        for _ in range(20):
            theta_candidate = theta_trial - trial_lr * step
            F0s_c = _all_F0s(ansatz_template, theta_old, theta_rhs, theta_candidate, lin_terms, shift_fwd, shift_bwd)
            signs_c = tracker.signs_at(theta_candidate, F0s_c)
            cost_candidate = -target_C0(ansatz_template, theta_old, theta_rhs, theta_candidate, amp_old, amp_rhs, dt, lin_terms, shift_fwd, shift_bwd, signs_c, F0s=F0s_c) ** 2
            if cost_candidate < cost_prev:
                found = True
                break
            trial_lr *= 0.5
        if not found:
            break
        theta_trial = theta_candidate
        cost_prev = cost_candidate
        lr = min(trial_lr * 1.5, 1.0)
    F0s = _all_F0s(ansatz_template, theta_old, theta_rhs, theta_trial, lin_terms, shift_fwd, shift_bwd)
    signs = tracker.signs_at(theta_trial, F0s)
    amp_new = target_C0(ansatz_template, theta_old, theta_rhs, theta_trial, amp_old, amp_rhs, dt, lin_terms, shift_fwd, shift_bwd, signs, F0s=F0s)
    return theta_trial, amp_new
