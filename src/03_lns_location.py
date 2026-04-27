"""
03_lns_location.py
===================
Large Neighborhood Search (LNS) pour le problème de localisation de lockers.

À chaque itération :
  - DESTROY : on retire aléatoirement q lockers de la solution courante
  - REPAIR  : on résout un petit MILP avec Gurobi pour choisir les q meilleurs
               lockers à remettre parmi les candidats restants
  - On accepte la nouvelle solution si elle est meilleure

Ce fichier utilise les MÊMES données que 01_gurobi_mnl_charnes_cooper.py
mais les résout via LNS — utile quand l'instance devient trop grande.

Dépendances :
    pip install gurobipy numpy
"""

import numpy as np
import gurobipy as gp
from gurobipy import GRB
import random
import time

# ─────────────────────────────────────────────
# 1. DONNÉES JOUET (identiques au fichier 01)
# ─────────────────────────────────────────────

np.random.seed(42)
random.seed(42)

n_zones   = 6
n_lockers = 10
n_compet  = 3
P         = 3    # nombre max de lockers à ouvrir

I = range(n_zones)
J = range(n_lockers)
C = range(n_compet)

coords_zones   = np.random.rand(n_zones,   2) * 100
coords_lockers = np.random.rand(n_lockers, 2) * 100
coords_compet  = np.random.rand(n_compet,  2) * 100

w        = np.random.randint(100, 1000, size=n_zones).astype(float)
A_locker = np.random.uniform(1, 5, size=n_lockers)
A_compet = np.random.uniform(1, 5, size=n_compet)
rho      = 2.0

def euclidean(a, b):
    return np.sqrt(np.sum((a - b)**2)) + 1e-6

dist_iz = np.array([[euclidean(coords_zones[i], coords_lockers[j])
                     for j in J] for i in I])
dist_ic = np.array([[euclidean(coords_zones[i], coords_compet[c])
                     for c in C] for i in I])

u   = np.array([[A_locker[j] / (dist_iz[i, j] ** rho) for j in J] for i in I])
u0  = np.array([sum(A_compet[c] / (dist_ic[i, c] ** rho) for c in C) for i in I])

# ─────────────────────────────────────────────
# 2. FONCTION D'ÉVALUATION (objectif MNL)
# ─────────────────────────────────────────────

def evaluate(solution: list[int]) -> float:
    """
    Calcule la part de marché totale capturée pour un ensemble de lockers ouverts.
    solution : liste des indices j des lockers ouverts
    """
    total = 0.0
    for i in I:
        S_i = sum(u[i, j] for j in solution)
        total += w[i] * S_i / (S_i + u0[i])
    return total

# ─────────────────────────────────────────────
# 3. SOLUTION INITIALE — Heuristique gloutonne
# ─────────────────────────────────────────────

def greedy_solution() -> list[int]:
    """
    Construit une solution en ajoutant à chaque étape
    le locker qui améliore le plus la part de marché.
    """
    solution = []
    candidats = list(J)

    for _ in range(P):
        meilleur_j   = None
        meilleur_gain = -1
        for j in candidats:
            gain = evaluate(solution + [j]) - evaluate(solution)
            if gain > meilleur_gain:
                meilleur_gain = gain
                meilleur_j    = j
        solution.append(meilleur_j)
        candidats.remove(meilleur_j)

    return solution

# ─────────────────────────────────────────────
# 4. REPAIR — Sous-problème Gurobi
# ─────────────────────────────────────────────

def repair(solution_fixee: list[int], candidats_libres: list[int], q: int) -> list[int]:
    """
    Étant donné :
      - solution_fixee : lockers qu'on garde (déjà dans la solution)
      - candidats_libres : lockers qu'on peut choisir pour remplacer les q retirés
      - q : nombre de lockers à choisir parmi les candidats_libres

    Résout un petit MILP Gurobi (Charnes-Cooper) pour trouver les q meilleurs.
    Retourne la nouvelle solution complète.
    """
    if not candidats_libres or q == 0:
        return solution_fixee

    J_free = candidats_libres
    theta_max = 1.0 / u0

    m = gp.Model("repair")
    m.Params.OutputFlag = 0     # silencieux
    m.Params.TimeLimit  = 10   # max 10 secondes par sous-problème

    y     = m.addVars(J_free, vtype=GRB.BINARY,     name="y")
    theta = m.addVars(I,      lb=0.0, ub=theta_max, name="theta")
    z     = m.addVars(I, J_free, lb=0.0,            name="z")

    # Contribution fixe des lockers déjà dans la solution
    u_fixe = np.array([sum(u[i, j] for j in solution_fixee) for i in I])

    # Objectif : maximiser la capture totale (fixe + libre)
    obj_fixe  = gp.quicksum(
        w[i] * u_fixe[i] * theta[i] for i in I
    )
    obj_libre = gp.quicksum(
        w[i] * u[i, j] * z[i, j] for i in I for j in J_free
    )
    m.setObjective(obj_fixe + obj_libre, GRB.MAXIMIZE)

    # Contrainte Charnes-Cooper (intégrant la contribution fixe)
    for i in I:
        m.addConstr(
            u_fixe[i] * theta[i]
            + gp.quicksum(u[i, k] * z[i, k] for k in J_free)
            + u0[i] * theta[i] == 1
        )

    # McCormick
    for i in I:
        for j in J_free:
            tmax = theta_max[i]
            m.addConstr(z[i, j] <= tmax * y[j])
            m.addConstr(z[i, j] <= theta[i])
            m.addConstr(z[i, j] >= theta[i] - tmax * (1 - y[j]))

    # Choisir exactement q lockers parmi les candidats libres
    m.addConstr(gp.quicksum(y[j] for j in J_free) == q)

    m.optimize()

    if m.Status in [GRB.OPTIMAL, GRB.TIME_LIMIT]:
        nouveaux = [j for j in J_free if y[j].X > 0.5]
        return solution_fixee + nouveaux
    else:
        # Si Gurobi échoue, on garde aléatoirement q candidats
        return solution_fixee + random.sample(J_free, min(q, len(J_free)))

# ─────────────────────────────────────────────
# 5. LNS — Boucle principale
# ─────────────────────────────────────────────

def lns(n_iterations: int = 50, q: int = 2) -> tuple[list[int], float]:
    """
    Large Neighborhood Search.
    n_iterations : nombre d'itérations LNS
    q            : nombre de lockers détruits/reconstruits à chaque itération
    """
    # Solution initiale gloutonne
    sol_courante = greedy_solution()
    val_courante = evaluate(sol_courante)
    sol_meilleure = sol_courante.copy()
    val_meilleure = val_courante

    print("\n" + "=" * 60)
    print("  LARGE NEIGHBORHOOD SEARCH")
    print("=" * 60)
    print(f"  Solution initiale (greedy) : lockers {sorted(sol_courante)}")
    print(f"  Valeur initiale            : {val_courante:.4f}")
    print(f"  Paramètres : {n_iterations} itérations, q={q} lockers détruits")
    print("-" * 60)

    debut = time.time()

    for it in range(n_iterations):

        # ── DESTROY : retirer q lockers aléatoirement ──────────────
        n_gardes   = P - q
        gardes     = random.sample(sol_courante, min(n_gardes, len(sol_courante)))
        retires    = [j for j in sol_courante if j not in gardes]
        candidats  = [j for j in J if j not in gardes]   # tout ce qu'on peut remettre

        # ── REPAIR : choisir q lockers parmi les candidats ─────────
        nouvelle_sol = repair(gardes, candidats, q=P - len(gardes))
        nouvelle_val = evaluate(nouvelle_sol)

        # ── ACCEPTATION : si amélioration ──────────────────────────
        if nouvelle_val > val_courante:
            amelioration = nouvelle_val - val_courante
            sol_courante = nouvelle_sol
            val_courante = nouvelle_val
            tag = f"✓ +{amelioration:.4f}"

            if nouvelle_val > val_meilleure:
                sol_meilleure = nouvelle_sol.copy()
                val_meilleure = nouvelle_val
                tag += " ★ NOUVEAU BEST"
        else:
            tag = "✗"

        if it % 10 == 0 or "★" in tag:
            print(f"  Iter {it+1:3d} | sol={sorted(sol_courante)} "
                  f"| val={val_courante:.4f} | {tag}")

    duree = time.time() - debut
    print("-" * 60)
    print(f"  Durée totale : {duree:.2f}s")
    return sol_meilleure, val_meilleure

# ─────────────────────────────────────────────
# 6. LANCEMENT
# ─────────────────────────────────────────────

if __name__ == "__main__":
    meilleure_sol, meilleure_val = lns(n_iterations=50, q=2)

    print("\n" + "=" * 60)
    print("  RÉSULTAT FINAL LNS")
    print("=" * 60)
    print(f"  Lockers ouverts      : {sorted(meilleure_sol)}")
    print(f"  Part de marché totale: {meilleure_val:.4f}")
    print(f"  Demande capturée     : {meilleure_val:.1f} / {w.sum():.1f}")
    print(f"  Part de marché (%)   : {meilleure_val/w.sum():.1%}")

    print("\n  Détail par zone :")
    for i in I:
        S_i  = sum(u[i, j] for j in meilleure_sol)
        ms_i = S_i / (S_i + u0[i])
        print(f"    Zone {i}: demande={w[i]:.0f}, part de marché={ms_i:.1%}")

    print("=" * 60)
    print("\n  Conseil : comparer avec le résultat exact de 01_gurobi_mnl_charnes_cooper.py")
    print("            pour mesurer la qualité de la solution LNS.")
