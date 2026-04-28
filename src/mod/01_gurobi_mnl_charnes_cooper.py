"""
================================
Exact resolution of the locker location problem with MNL objective.
Method: Charnes-Cooper transformation + McCormick inequalities → MILP

Toy instance:
    - 6 demand zones (I)
    - 10 candidate locker sites (J)
    - 3 competitor facilities (C)
    - P = 3 maximum lockers to open
"""

import numpy as np
import gurobipy as gp
from gurobipy import GRB

# ─────────────────────────────────────────────
# 1. TOY DATA
# ─────────────────────────────────────────────

np.random.seed(42)

# Sets
n_zones   = 6    # |I|
n_lockers = 10   # |J|
n_compet  = 3    # |C|
P         = 3    # max number of lockers to open

I = range(n_zones)
J = range(n_lockers)
C = range(n_compet)

# Random coordinates on a 100x100 km grid
coords_zones   = np.random.rand(n_zones,   2) * 100
coords_lockers = np.random.rand(n_lockers, 2) * 100
coords_compet  = np.random.rand(n_compet,  2) * 100

# Demand for each zone (population / expected parcels)
w = np.random.randint(100, 1000, size=n_zones).astype(float)

# Intrinsic attractiveness of lockers and competitors
A_locker = np.random.uniform(1, 5, size=n_lockers)
A_compet = np.random.uniform(1, 5, size=n_compet)

# Distance decay exponent (power law)
rho = 2.0

# Euclidean distance (with small epsilon to avoid division by zero)
def euclidean(a, b):
    return np.sqrt(np.sum((a - b)**2)) + 1e-6

# Distance matrices
dist_ij = np.array([[euclidean(coords_zones[i], coords_lockers[j])
                     for j in J] for i in I])
dist_ic = np.array([[euclidean(coords_zones[i], coords_compet[c])
                     for c in C] for i in I])

# Utility: u_ij = A_j / d_ij^rho  (Huff gravity model)
u = np.array([[A_locker[j] / (dist_ij[i, j] ** rho)
               for j in J] for i in I])

# Competitor baseline for each zone: u0_i = Σ_c A_c / d_ic^rho
u0 = np.array([sum(A_compet[c] / (dist_ic[i, c] ** rho) for c in C)
               for i in I])

# Upper bound on theta_i: when no locker is open, θ_i = 1/u0_i
theta_max = 1.0 / u0

print("=" * 55)
print("  TOY INSTANCE")
print("=" * 55)
print(f"  Demand zones       : {n_zones}")
print(f"  Candidate lockers  : {n_lockers}")
print(f"  Competitors        : {n_compet}")
print(f"  Budget (P)         : {P} lockers max")
print(f"  Total demand       : {w.sum():.0f}")
print("=" * 55)

# ─────────────────────────────────────────────
# 2. BUILD GUROBI MODEL
# ─────────────────────────────────────────────

model = gp.Model("MNL_Lockers_CharnesCooper")
model.Params.OutputFlag = 1
model.Params.MIPGap    = 1e-4
model.Params.TimeLimit = 120

# --- Decision variables ---

# y_j ∈ {0,1}: open locker at site j?
y = model.addVars(J, vtype=GRB.BINARY, name="y")

# theta_i ≥ 0: inverse of MNL denominator = 1 / (S_i + u0_i)
theta = model.addVars(I, lb=0.0, ub=theta_max, vtype=GRB.CONTINUOUS, name="theta")

# z_ij ≥ 0: linearization of y_j * theta_i (McCormick)
z = model.addVars(I, J, lb=0.0, vtype=GRB.CONTINUOUS, name="z")

# --- Linearized objective ---
# max Σ_i w_i * Σ_j u_ij * z_ij
model.setObjective(
    gp.quicksum(w[i] * u[i, j] * z[i, j] for i in I for j in J),
    GRB.MAXIMIZE
)

# ─────────────────────────────────────────────
# 3. CONSTRAINTS
# ─────────────────────────────────────────────

# (CC) Charnes-Cooper constraint: Σ_k u_ik * z_ik + u0_i * theta_i = 1
# Derived from θ_i * (S_i + u0_i) = 1, substituting z_ij = y_j * theta_i
for i in I:
    model.addConstr(
        gp.quicksum(u[i, k] * z[i, k] for k in J) + u0[i] * theta[i] == 1,
        name=f"CC_{i}"
    )

# (M1–M4) McCormick inequalities: linearize z_ij = y_j * theta_i
# where y_j ∈ {0,1} and 0 ≤ theta_i ≤ theta_max[i]
for i in I:
    for j in J:
        tmax = theta_max[i]
        model.addConstr(z[i, j] <= tmax * y[j],                    name=f"M1_{i}_{j}")
        model.addConstr(z[i, j] <= theta[i],                       name=f"M2_{i}_{j}")
        model.addConstr(z[i, j] >= theta[i] - tmax * (1 - y[j]),   name=f"M3_{i}_{j}")
        # z_ij >= 0 already enforced by lb=0

# (P) Budget: open at most P lockers
model.addConstr(gp.quicksum(y[j] for j in J) <= P, name="budget")

# ─────────────────────────────────────────────
# 4. SOLVE
# ─────────────────────────────────────────────

model.optimize()

# ─────────────────────────────────────────────
# 5. RESULTS
# ─────────────────────────────────────────────

if model.Status in [GRB.OPTIMAL, GRB.TIME_LIMIT]:
    print("\n" + "=" * 55)
    print("  RESULTS")
    print("=" * 55)

    open_lockers = [j for j in J if y[j].X > 0.5]
    print(f"\n  Open lockers : {open_lockers}")

    total_captured = 0.0
    for i in I:
        S_i    = sum(u[i, j] * y[j].X for j in J)
        ms_i   = S_i / (S_i + u0[i])
        cap_i  = w[i] * ms_i
        total_captured += cap_i
        print(f"  Zone {i}: demand={w[i]:.0f}, S_i={S_i:.4f}, "
              f"market share={ms_i:.1%}, captured={cap_i:.1f}")

    print(f"\n  Total captured demand : {total_captured:.1f}")
    print(f"  Total demand          : {w.sum():.1f}")
    print(f"  Overall market share  : {total_captured/w.sum():.1%}")
    print(f"\n  Gurobi objective value: {model.ObjVal:.6f}")
    print(f"  MIP Gap               : {model.MIPGap:.2%}")
    print("=" * 55)
else:
    print(f"Gurobi status: {model.Status} — no solution found.")
