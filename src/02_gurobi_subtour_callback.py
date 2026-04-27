"""
02_gurobi_subtour_callback.py
==============================
VRP (Vehicle Routing Problem) entre clusters avec élimination
des sous-tours par Lazy Constraints (callback Gurobi).

Problème :
    Trouver la tournée de coût minimal pour un camion qui part
    du dépôt (nœud 0), visite tous les clusters actifs une fois,
    et revient au dépôt — SANS sous-tour.

Données jouet :
    - 1 dépôt + 5 clusters (6 nœuds au total)
    - Distances euclidiennes aléatoires

Dépendances :
    pip install gurobipy numpy networkx
"""

import numpy as np
import gurobipy as gp
from gurobipy import GRB
import networkx as nx

# ─────────────────────────────────────────────
# 1. DONNÉES JOUET
# ─────────────────────────────────────────────

np.random.seed(7)

n_nodes = 6          # nœud 0 = dépôt, nœuds 1..5 = clusters
nodes   = list(range(n_nodes))
depot   = 0
clusters = list(range(1, n_nodes))

# Coordonnées aléatoires (grille 100x100 km)
coords = np.random.rand(n_nodes, 2) * 100

# Matrice de distances
def dist(a, b):
    return np.sqrt(np.sum((coords[a] - coords[b])**2))

cost = {(i, j): dist(i, j) for i in nodes for j in nodes if i != j}

print("=" * 50)
print("  VRP — CLUSTERS À VISITER")
print("=" * 50)
print(f"  Dépôt    : nœud {depot}")
print(f"  Clusters : {clusters}")
print("  Coordonnées :")
for n in nodes:
    label = "dépôt" if n == depot else f"cluster {n}"
    print(f"    Nœud {n} ({label}) : ({coords[n,0]:.1f}, {coords[n,1]:.1f})")
print("=" * 50)

# ─────────────────────────────────────────────
# 2. MODÈLE GUROBI
# ─────────────────────────────────────────────

model = gp.Model("VRP_Subtour_Callback")
model.Params.OutputFlag    = 1
model.Params.LazyConstraints = 1   # OBLIGATOIRE pour utiliser cbLazy

# Variables d'arc : x[i,j] = 1 si le camion va de i vers j
x = model.addVars(
    [(i, j) for i in nodes for j in nodes if i != j],
    vtype=GRB.BINARY,
    name="x"
)

# Objectif : minimiser la distance totale
model.setObjective(
    gp.quicksum(cost[i, j] * x[i, j] for i in nodes for j in nodes if i != j),
    GRB.MINIMIZE
)

# ─────────────────────────────────────────────
# 3. CONTRAINTES DE BASE
# ─────────────────────────────────────────────

# Chaque nœud est quitté exactement une fois
for i in nodes:
    model.addConstr(
        gp.quicksum(x[i, j] for j in nodes if j != i) == 1,
        name=f"depart_{i}"
    )

# Chaque nœud est arrivé exactement une fois
for j in nodes:
    model.addConstr(
        gp.quicksum(x[i, j] for i in nodes if i != j) == 1,
        name=f"arrivee_{j}"
    )

# ─────────────────────────────────────────────
# 4. CALLBACK — ÉLIMINATION DES SOUS-TOURS
# ─────────────────────────────────────────────

def subtour_callback(model, where):
    """
    Appelé par Gurobi à chaque solution entière candidate.
    On vérifie s'il y a des sous-tours et on ajoute des coupes si oui.
    """
    if where != GRB.Callback.MIPSOL:
        return

    # Récupérer les valeurs des variables d'arc dans la solution courante
    x_vals = model.cbGetSolution(model._x)

    # Construire le graphe de la tournée candidate
    arcs_actifs = [(i, j) for (i, j), v in x_vals.items() if v > 0.5]
    G = nx.DiGraph(arcs_actifs)

    # Détecter les composantes fortement connexes (= sous-tours potentiels)
    composantes = list(nx.strongly_connected_components(G))

    sous_tours_trouves = 0
    for comp in composantes:
        # Un sous-tour est une composante qui ne contient PAS le dépôt
        if depot not in comp and len(comp) >= 2:
            sous_tours_trouves += 1
            print(f"    [Callback] Sous-tour détecté : {sorted(comp)} — coupe ajoutée")

            # Coupe : dans ce sous-ensemble, on ne peut pas avoir |comp| arcs
            # (ça formerait un cycle fermé sans passer par le dépôt)
            model.cbLazy(
                gp.quicksum(
                    model._x[i, j]
                    for i in comp
                    for j in comp
                    if i != j
                ) <= len(comp) - 1
            )

    if sous_tours_trouves == 0:
        print(f"    [Callback] Solution valide trouvée — pas de sous-tour")

# Attacher les variables au modèle pour y accéder dans le callback
model._x = x

# ─────────────────────────────────────────────
# 5. RÉSOLUTION
# ─────────────────────────────────────────────

model.optimize(subtour_callback)

# ─────────────────────────────────────────────
# 6. RÉSULTATS
# ─────────────────────────────────────────────

if model.Status in [GRB.OPTIMAL, GRB.TIME_LIMIT]:
    print("\n" + "=" * 50)
    print("  TOURNÉE OPTIMALE")
    print("=" * 50)

    # Reconstruire la tournée depuis le dépôt
    x_sol = {(i, j): x[i, j].X for i in nodes for j in nodes if i != j}
    tournee = [depot]
    noeud_actuel = depot
    for _ in range(n_nodes - 1):
        for j in nodes:
            if j != noeud_actuel and x_sol.get((noeud_actuel, j), 0) > 0.5:
                tournee.append(j)
                noeud_actuel = j
                break
    tournee.append(depot)  # retour au dépôt

    print(f"\n  Tournée : {' → '.join(str(n) for n in tournee)}")
    print(f"  Distance totale : {model.ObjVal:.2f} km")
    print("=" * 50)
else:
    print(f"Statut Gurobi : {model.Status}")
