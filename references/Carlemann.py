import pennylane as qml
import numpy as np
import math
import matplotlib.pyplot as plt
qml.drawer.use_style('black_white')
from functools import reduce

class Burgers_Carlemann:
    def __init__(self, N, N_T, total_time, mu, dt, u0, uN1, stencil='method_2', dtype=np.float64):
        super(Burgers_Carlemann, self).__init__()
        self.N = N
        self.N_T = N_T
        self.TOTAL_TIME = total_time
        self.MU = mu
        self.DT = dt
        self.U0 = u0
        self.UN1 = uN1
        self.DTYPE = dtype
        self.STENCIL = stencil
        '''
        Write notes here.
        '''
        return 
        
    def get_x_dx(self):
        x = np.linspace(0, 1, self.N+2, dtype=self.DTYPE)
        dx = x[1] - x[0]
        return x, dx
    
    def get_n_timesteps(self):
        n_timesteps = int(np.round(self.TOTAL_TIME/self.DT))
        return n_timesteps

    def get_init_state(self):
        x, dx = self.get_x_dx()
        psi_init = np.sin(2*np.pi*x)
        return psi_init
    
    def get_u_desired(self):
        x, dx = self.get_x_dx()
        # Classical testing
        n_timesteps = int(np.round(self.TOTAL_TIME/self.DT))
        #x_plot = np.linspace(0, 1, N)#[:-1]
        #t_plot = np.arange(0, self.TOTAL_TIME, self.DT)
        u = np.zeros((self.N+2, n_timesteps+1), dtype=self.DTYPE)
        u[:, 0] = np.sin(2*np.pi*x)
        # Forward in time central in space
        for j in range(n_timesteps):
            for i in range(1, self.N+1):
                if self.STENCIL == 'method_1':
                    t = (self.DT/(4*dx))*(u[i+1, j]**2 - u[i-1, j]**2)
                elif self.STENCIL == 'method_2':
                    t = (self.DT/(2*dx))*u[i, j]*(u[i+1, j] - u[i-1, j])
                u[i, j+1] = (u[i, j] + 
                (self.MU*self.DT/(dx**2))*(u[i+1, j] - 2*u[i, j] + u[i-1, j]) - 
                t
                )
        return u
    
    def construct_F2_matrix(self, n):
        """Constructs the F matrix for Carleman linearization given dy_i/dt = y_(i+1)^2 - y_(i-1)^2."""
        F = np.zeros((n, n**2), dtype=self.DTYPE)  # Shape (n, n^2)

        def index(i, j, n):
            """Maps (i, j) in y⊗2 to the corresponding index in flattened form (0-based)."""
            return (i-1) * n + (j-1)  # 0-based indexing

        if self.STENCIL == 'method_1':
            for i in range(1, n+1):  # 1-based indexing for y_i
                if i + 1 <= n:  # y_(i+1)^2 term
                    F[i-1, index(i+1, i+1, n)] = 1
                if i - 1 >= 1:  # y_(i-1)^2 term
                    F[i-1, index(i-1, i-1, n)] = -1
        elif self.STENCIL == 'method_2':
            for i in range(1, n+1):  # 1-based indexing for y_i
                if i + 1 <= n:  # y_i*y_(i+1) term
                    F[i-1, index(i, i+1, n)] = 1
                if i - 1 >= 1:  # y_i*y_(i-1) term
                    F[i-1, index(i, i-1, n)] = -1
        return F
    
    def get_a_b(self):
        x, dx = self.get_x_dx()
        a = self.MU/(dx**2)
        if self.STENCIL == 'method_1':
            b = -1/(4*dx)
        elif self.STENCIL == 'method_2':
            b = -1/(2*dx)
        return a, b
    
    def get_Fs(self):
        a, b = self.get_a_b()
        # F0
        F0 = np.zeros((self.N, 1), dtype=self.DTYPE)
        F0[0, 0] = a*self.U0 - b*(self.U0**2)
        F0[-1, 0] = a*self.UN1 + b*(self.UN1**2)
        # F1
        F1 = np.zeros((self.N, self.N), dtype=self.DTYPE)
        for i in range(self.N):
            if i == 0:
                F1[i, i] = -2*a
                F1[i, i+1] = a
            if i >0 and i < self.N-1:
                F1[i, i-1] = a
                F1[i, i] = -2*a
                F1[i, i+1] = a
            if i == self.N-1:
                F1[i, i-1] = a
                F1[i, i] = -2*a
        # F2
        F2 = self.construct_F2_matrix(self.N)
        F2 = F2*b
        return F0, F1, F2
    
    def kronecker_identity(self, d, n):
        I = np.eye(d, dtype=self.DTYPE)
        return reduce(np.kron, [I] * n)
    
    def get_A_ij(self, F0, F1, F2, j):
        A_j_jm1 = np.zeros((self.N**j, self.N**(j-1)), dtype=self.DTYPE)
        A_j_j = np.zeros((self.N**j, self.N**j), dtype=self.DTYPE)
        A_j_jp1 = np.zeros((self.N**j, self.N**(j+1)), dtype=self.DTYPE)
        for i in range(j):
            if i ==0:
                t2 = self.kronecker_identity(self.N, j-i-1)
                A_j_jm1 += np.kron(F0, t2)
                A_j_j += np.kron(F1, t2)
                A_j_jp1 += np.kron(F2, t2)
            if i>0 and i<(j-1):
                t1 = self.kronecker_identity(self.N, i)
                t2 = self.kronecker_identity(self.N, j-i-1)
                A_j_jm1 += np.kron(t1, np.kron(F0, t2))
                A_j_j += np.kron(t1, np.kron(F1, t2))
                A_j_jp1 += np.kron(t1, np.kron(F2, t2))
            if i==j-1:
                t1 = self.kronecker_identity(self.N, i)
                A_j_jm1 += np.kron(t1, F0)
                A_j_j += np.kron(t1, F1)
                A_j_jp1 += np.kron(t1, F2)
        return A_j_jm1, A_j_j, A_j_jp1
    
    def geometric_series(self, N, i):
        t = 0
        for j in range(1, i+1):
            t += self.N**j
        return t
    
    def get_A(self,):
        a, b = self.get_a_b()
        Dim = self.geometric_series(self.N, self.N_T)
        F0, F1, F2 = self.get_Fs()
        A = np.zeros((Dim, Dim), dtype=self.DTYPE)
        for i in range(1, self.N_T+1):
            if i == 1:
                r_min = 0
                r_max = self.geometric_series(self.N, i)
                c_min = 0
                c_max = self.geometric_series(self.N, i)
                A[r_min : r_max, c_min : c_max] = F1
                c_min = self.geometric_series(self.N, i)
                c_max = self.geometric_series(self.N, i+1)
                A[r_min : r_max, c_min : c_max] = F2
            if i>1 and i<self.N_T:
                A_j_jm1, A_j_j, A_j_jp1 = self.get_A_ij(F0, F1, F2, i)
                r_min = self.geometric_series(self.N, i-1)
                r_max = self.geometric_series(self.N, i)
                c_min = self.geometric_series(self.N, i-2)
                c_max = self.geometric_series(self.N, i-1)
                A[r_min : r_max, c_min : c_max] = A_j_jm1
                c_min = self.geometric_series(self.N, i-1)
                c_max = self.geometric_series(self.N, i)
                A[r_min : r_max, c_min : c_max] = A_j_j
                c_min = self.geometric_series(self.N, i)
                c_max = self.geometric_series(self.N, i+1)
                A[r_min : r_max, c_min : c_max] = A_j_jp1
            if i == self.N_T:
                A_j_jm1, A_j_j, A_j_jp1 = self.get_A_ij(F0, F1, F2, i)
                r_min = self.geometric_series(self.N, i-1)
                r_max = self.geometric_series(self.N, i)
                c_min = self.geometric_series(self.N, i-2)
                c_max = self.geometric_series(self.N, i-1)
                A[r_min : r_max, c_min : c_max] = A_j_jm1
                c_min = self.geometric_series(self.N, i-1)
                c_max = self.geometric_series(self.N, i)
                A[r_min : r_max, c_min : c_max] = A_j_j
        return A
    
    def kronecker_y(self, y, n):
        return reduce(np.kron, [y] * n)
    
    def get_B(self):
        a, b = self.get_a_b()
        Dim = self.geometric_series(self.N, self.N_T)
        F0, F1, F2 = self.get_Fs()
        b = np.zeros((Dim), dtype=self.DTYPE)
        b[:self.N] = F0[:, 0]
        return b
    
    def get_y_init(self):
        Dim = self.geometric_series(self.N, self.N_T)
        u = self.get_u_desired()
        y_init = np.zeros((Dim), dtype=self.DTYPE)
        t = u[1:-1, 0]
        for i in range(1, self.N_T+1):
            r_min = self.geometric_series(self.N, i-1)
            r_max = self.geometric_series(self.N, i)
            if i == 1:
                y_init[r_min : r_max] = t
            if i>1:
                y_init[r_min : r_max] = self.kronecker_y(t, i)
        return y_init
    
    def get_I_m_Adt(self):
        Dim = self.geometric_series(self.N, self.N_T)
        A_t = self.get_A()
        A = np.eye(Dim, dtype=self.DTYPE) - A_t*self.DT
        return A
    
    def get_I_p_Adt(self):
        Dim = self.geometric_series(self.N, self.N_T)
        A_t = self.get_A()
        A = np.eye(Dim, dtype=self.DTYPE) + A_t*self.DT
        return A
    
    def get_implicit_solver(self):
        y_init = self.get_y_init()
        n_timesteps = int(np.round(self.TOTAL_TIME/self.DT))
        A = self.get_I_m_Adt()
        B = self.get_B()
        u = self.get_u_desired()
        y_store = []
        RMSE_list = []
        t = np.concat(([self.U0], y_init[:self.N], [self.UN1]), dtype=self.DTYPE)
        y_prev = y_init.copy()
        y_store.append(t)
        for i in range(n_timesteps):
            print(f"Time step {i+1}/{n_timesteps}")
            L = y_prev + B*self.DT
            y_prev = np.linalg.solve(A, L)
            t = np.sum((y_prev[:self.N] - u[1:-1, i+1])**2)
            t = np.sqrt(t/self.N)
            RMSE_list.append(t)
            t = np.concat(([self.U0], y_prev[:self.N], [self.UN1]), dtype=self.DTYPE)
            y_store.append(t)
        RMSE_list = np.array(RMSE_list)
        return y_store, RMSE_list
    
    def get_explicit_solver(self):
        y_init = self.get_y_init()
        n_timesteps = int(np.round(self.TOTAL_TIME/self.DT))
        A = self.get_I_p_Adt()
        B = self.get_B()
        u = self.get_u_desired()
        y_store = []
        RMSE_list = []
        t = np.concat(([self.U0], y_init[:self.N], [self.UN1]), dtype=self.DTYPE)
        y_prev = y_init.copy()
        y_store.append(t)
        for i in range(n_timesteps):
            print(f"Time step {i+1}/{n_timesteps}")
            y_prev = A@y_prev + B*self.DT
            t = np.sum((y_prev[:self.N] - u[1:-1, i+1])**2)
            t = np.sqrt(t/self.N)
            RMSE_list.append(t)
            t = np.concat(([self.U0], y_prev[:self.N], [self.UN1]), dtype=self.DTYPE)
            y_store.append(t)
        RMSE_list = np.array(RMSE_list)
        return y_store, RMSE_list
    

    def get_implicit_solver_modify(self):
        y_init = self.get_y_init()
        n_timesteps = int(np.round(self.TOTAL_TIME/self.DT))
        A = self.get_I_m_Adt()
        B = self.get_B()
        u = self.get_u_desired()
        y_store = []
        RMSE_list = []
        t = np.concat(([self.U0], y_init[:self.N], [self.UN1]), dtype=self.DTYPE)
        y_prev = y_init.copy()
        y_store.append(t)
        for i in range(n_timesteps):
            print(f"Time step {i+1}/{n_timesteps}")
            L = y_prev + B*self.DT
            #y_prev = np.linalg.solve(A, L)
            # Quantum solution for Ax = L
            # QSVT Pennylane
            t = np.sum((y_prev[:self.N] - u[1:-1, i+1])**2)
            t = np.sqrt(t/self.N)
            RMSE_list.append(t)
            t = np.concat(([self.U0], y_prev[:self.N], [self.UN1]), dtype=self.DTYPE)
            y_store.append(t)
        RMSE_list = np.array(RMSE_list)
        return y_store, RMSE_list

    # Default pennylane QSVT
    def get_n_wires_default(self, L):
        n_wires = math.ceil(math.log2(L.shape[0])) + 1
        block_encode = qml.BlockEncode(L.T, wires=range(n_wires))
        factor = block_encode.hyperparameters["norm"]
        return n_wires, block_encode, factor

    def get_scaled_matrix(self, L):
        L_scaled = L/np.linalg.norm(L, 2)
        return L_scaled
    
    def get_singular_values_default(self):
        scaled_matrix = self.get_scaled_data()
        t1 = np.linalg.norm(scaled_matrix@(np.conj(scaled_matrix).T), ord=np.inf)
        t2 = np.linalg.norm(np.conj(scaled_matrix).T@scaled_matrix, ord=np.inf)
        scale_parameter = np.max((t1, t2))
        t = scaled_matrix/scale_parameter
        singular_values = np.linalg.svd(t, compute_uv=False)
        return singular_values

    def get_block_encoded_default(self, L):
        n_wires, block_encode, factor = self.get_n_wires_default(L)
        t = block_encode.matrix()[:L.shape[0], :L.shape[1]]
        block_encode = t*factor
        return block_encode
    
    def get_A_inv_default_circuit(self, phi, s):
        n_wires, block_encode, factor = self.get_n_wires_default()
        projectors = [
            qml.PCPhase(phi[i], dim=len(self.A), wires=range(n_wires))
            for i in range(len(phi))
        ]
        qml.QSVT(block_encode, projectors)
        return qml.state()
    
    def get_A_inv_default(self, phi, s):
        n_wires, block_encode, factor = self.get_n_wires_default()
        t = qml.matrix(self.get_A_inv_default_circuit, wire_order=range(n_wires))(phi, s)
        t = t[:self.A.shape[0], :self.A.shape[1]]
        A_inv_default = t/(s*factor)
        return A_inv_default
    
    def get_A_inv_psi_default_circuit(self, L, phi, psi_normalized):
        # Assuming square matrix
        n_wires, block_encode, factor = self.get_n_wires_default(L)
        projectors = [
            qml.PCPhase(phi[i], dim=len(L), wires=range(n_wires))
            for i in range(len(phi))
        ]
        qml.StatePrep(psi_normalized, wires=range(1, 6))
        qml.QSVT(block_encode, projectors)
        return qml.state()

    def get_A_inv_psi_default(self, L, psi_state, phi, s):
        psi_norm = np.linalg.norm(psi_state, 2)
        psi_normalized = psi_state/psi_norm
        n_wires, block_encode, factor = self.get_n_wires_default(L)
        dev = qml.device("default.qubit", wires=range(n_wires))
        circuit = qml.QNode(self.get_A_inv_psi_default_circuit, dev)
        t = circuit(L, phi, psi_normalized)
        #t = np.real(t[:psi_normalized.shape[0]])
        t = t[:psi_normalized.shape[0]]
        state_inverse_default = t*(psi_norm)/(s*factor)
        return state_inverse_default