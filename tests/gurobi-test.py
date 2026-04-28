import gurobipy as gp

# Test rapide
try:
    m = gp.Model("test")
    print("Gurobi est bien installé et la licence est active !")
except gp.GurobiError as e:
    print(f"Erreur Gurobi : {e}")
except ImportError:
    print("La bibliothèque gurobipy n'est pas trouvée.")