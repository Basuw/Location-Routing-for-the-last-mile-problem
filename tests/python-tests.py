import numpy as np
import matplotlib.pyplot as plt

# Générer 10 000 nombres aléatoires uniformes entre 1 et 5
np.random.seed(42)
valeurs = np.random.uniform(1, 5, size=10000)

# Créer une figure avec 2 sous-graphiques
fig, axes = plt.subplots(1, 2, figsize=(12, 4))

# 1. Histogramme
axes[0].hist(valeurs, bins=50, color='skyblue', edgecolor='black', alpha=0.7)
axes[0].set_xlabel('Valeurs')
axes[0].set_ylabel('Fréquence')
axes[0].set_title('Distribution uniforme np.random.uniform(1, 5)')
axes[0].grid(axis='y', alpha=0.3)

# 2. Courbe de distribution (density plot)
axes[1].hist(valeurs, bins=50, density=True, color='lightcoral', 
             edgecolor='black', alpha=0.7, label='Histogramme')
# Ajouter une ligne théorique pour la distribution uniforme
x = np.linspace(0.5, 5.5, 100)
y = np.where((x >= 1) & (x <= 5), 1/4, 0)  # Probabilité = 1/(5-1) = 0.25
axes[1].plot(x, y, 'b-', linewidth=2, label='Distribution théorique')
axes[1].set_xlabel('Valeurs')
axes[1].set_ylabel('Densité de probabilité')
axes[1].set_title('Distribution uniforme (Density)')
axes[1].legend()
axes[1].grid(alpha=0.3)

print(f"Min: {valeurs.min():.4f}")
print(f"Max: {valeurs.max():.4f}")
print(f"Moyenne: {valeurs.mean():.4f}")
print(f"Écart-type: {valeurs.std():.4f}")

plt.tight_layout()
#plt.savefig('distribution_uniforme.png', dpi=100, bbox_inches='tight')
plt.show()

