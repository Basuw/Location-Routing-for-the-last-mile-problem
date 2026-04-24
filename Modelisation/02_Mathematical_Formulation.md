# Formulation Mathématique — LRP avec Lockers Stationnaires et MNL

## 1. Indices et Ensembles

| Symbole | Description |
|---|---|
| $i \in I$ | Zones de demande (clients agrégés par zone géographique) |
| $j \in J$ | Sites candidats pour l'ouverture de lockers |
| $c \in C$ | Lockers/agences des **concurrents** (positions fixes) |
| $k \in K$ | **Clusters** (zones géographiques regroupant des sites candidats) |
| $J_k \subseteq J$ | Sites candidats appartenant au cluster $k$ |
| $v \in V_T$ | Camions disponibles |
| $v \in V_M$ | Motos disponibles |
| $0$ | Indice du dépôt central |

---

## 2. Paramètres

### Demande et géographie

| Symbole | Description |
|---|---|
| $d_i > 0$ | Demande totale (nombre de colis/clients) dans la zone $i$ |
| $\text{dist}_{ij} \geq 0$ | Distance entre la zone $i$ et le site locker $j$ |
| $\text{dist}_{ic} \geq 0$ | Distance entre la zone $i$ et le locker concurrent $c$ |
| $\text{dist}_{kl} \geq 0$ | Distance entre les clusters $k$ et $l$ (entre hubs) |
| $\text{dist}_{jj'} \geq 0$ | Distance entre les sites $j$ et $j'$ à l'intérieur d'un cluster |

### Modèle d'attractivité (MNL)

| Symbole | Description |
|---|---|
| $\alpha_j$ | Attractivité intrinsèque du locker $j$ (qualité, taille, réputation) |
| $\beta > 0$ | Paramètre de sensibilité à la distance (à calibrer sur les données) |
| $\gamma_c$ | Attractivité intrinsèque du concurrent $c$ (fixée) |
| $\mu_0$ | Utilité de l'option extérieure (ne rien utiliser) |
| $a_{ij} = e^{\,\alpha_j - \beta \cdot \text{dist}_{ij}}$ | **Attractivité** du locker $j$ pour la zone $i$ |
| $b_{ic} = e^{\,\gamma_c - \beta \cdot \text{dist}_{ic}}$ | **Attractivité** du concurrent $c$ pour la zone $i$ (exogène) |
| $a_{i0} = e^{\mu_0}$ | Attractivité de l'option extérieure (exogène) |
| $B_c^i = \sum_{c \in C} b_{ic} + a_{i0}$ | Attractivité totale **fixe** (concurrents + option extérieure) pour la zone $i$ |

### Coûts et capacités

| Symbole | Description |
|---|---|
| $f_j \geq 0$ | Coût fixe d'ouverture du locker $j$ |
| $\text{cap}_j$ | Capacité (nombre de colis) du locker $j$ |
| $\tau^T_{kl}$ | Coût de transport camion entre les clusters $k$ et $l$ |
| $\tau^M_{jj'}$ | Coût de transport moto entre les sites $j$ et $j'$ |
| $Q_T$ | Capacité de chargement d'un camion |
| $Q_M$ | Capacité de chargement d'une moto |
| $B$ | Budget total disponible |

---

## 3. Variables de Décision

### Localisation

$$x_j \in \{0, 1\}, \quad \forall j \in J$$

> $x_j = 1$ si le locker $j$ est ouvert, $0$ sinon.

### Routage niveau 1 — Camions (inter-clusters)

$$u_{kl}^v \in \{0, 1\}, \quad \forall k, l \in K \cup \{0\},\ k \neq l,\ \forall v \in V_T$$

> $u_{kl}^v = 1$ si le camion $v$ emprunte l'arc $k \to l$.

$$s_k^v \geq 0, \quad \forall k \in K,\ \forall v \in V_T$$

> Variable de position dans la tournée (anti-sous-tours, Miller–Tucker–Zemlin).

### Routage niveau 2 — Motos (intra-cluster)

$$w_{jj'}^v \in \{0, 1\}, \quad \forall j, j' \in J_k,\ j \neq j',\ \forall v \in V_M$$

> $w_{jj'}^v = 1$ si la moto $v$ emprunte l'arc $j \to j'$ dans le cluster.

### Variables auxiliaires (linéarisation MNL)

$$p_{ij} \geq 0, \quad \forall i \in I,\ \forall j \in J$$

> Part de la demande de la zone $i$ capturée par le locker $j$ (à déterminer par le modèle).

$$z_{ij} \geq 0, \quad \forall i \in I,\ \forall j \in J$$

> Variable de linéarisation : $z_{ij} \approx p_{ij} \cdot x_j$ (produit d'une variable continue et d'une binaire).

---

## 4. Fonction Objectif

### 4.1 Part de marché capturée (formulation MNL)

La probabilité qu'un client de la zone $i$ choisisse le locker $j$ **s'il est ouvert** est donnée par le MNL :

$$P_{ij}(\mathbf{x}) = \frac{x_j \cdot a_{ij}}{\displaystyle\sum_{j' \in J} x_{j'} \cdot a_{ij'} + B_c^i}$$

La demande totale capturée par notre réseau est :

$$\text{MS}(\mathbf{x}) = \sum_{i \in I} d_i \sum_{j \in J} P_{ij}(\mathbf{x}) = \sum_{i \in I} \frac{d_i \cdot \displaystyle\sum_{j \in J} x_j \cdot a_{ij}}{\displaystyle\sum_{j' \in J} x_{j'} \cdot a_{ij'} + B_c^i}$$

### 4.2 Objectif global (maximisation du profit ou de la part de marché nette)

$$\max \quad Z = \underbrace{\sum_{i \in I} \frac{d_i \cdot \displaystyle\sum_{j \in J} x_j \cdot a_{ij}}{\displaystyle\sum_{j' \in J} x_{j'} \cdot a_{ij'} + B_c^i}}_{\text{part de marché capturée}} - \underbrace{\sum_{j \in J} f_j \cdot x_j}_{\text{coûts fixes lockers}} - \underbrace{\sum_{v \in V_T} \sum_{k,l} \tau^T_{kl} \cdot u_{kl}^v}_{\text{coûts camions}} - \underbrace{\sum_{v \in V_M} \sum_{j,j'} \tau^M_{jj'} \cdot w_{jj'}^v}_{\text{coûts motos}}$$

> **Note** : La fonction objectif est une **somme de fractions** (problème linéaire-fractionnaire multi-ratio, MLFP). Elle n'est pas linéaire — une reformulation est nécessaire pour Gurobi (voir Section 7).

---

## 5. Contraintes de Localisation

### Budget

$$\sum_{j \in J} f_j \cdot x_j \leq B \tag{C1}$$

### Nombre maximal de lockers ouverts (optionnel)

$$\sum_{j \in J} x_j \leq N_{\max} \tag{C2}$$

### Capacité des lockers

La demande totale affectée au locker $j$ ne doit pas dépasser sa capacité :

$$\sum_{i \in I} d_i \cdot p_{ij} \leq \text{cap}_j \cdot x_j, \quad \forall j \in J \tag{C3}$$

### Un cluster doit avoir au moins un locker ouvert pour être actif

On définit $y_k \in \{0,1\}$ : cluster $k$ actif ($y_k = 1$) si au moins un locker de ce cluster est ouvert.

$$x_j \leq y_k, \quad \forall k \in K,\ \forall j \in J_k \tag{C4}$$

$$y_k \leq \sum_{j \in J_k} x_j, \quad \forall k \in K \tag{C5}$$

---

## 6. Contraintes de Routage — Niveau 1 (Camions, inter-clusters)

Chaque cluster actif doit être visité par exactement un camion.

### Conservation de flux (entrée = sortie pour chaque nœud)

$$\sum_{l \in K \cup \{0\},\, l \neq k} u_{lk}^v = \sum_{l \in K \cup \{0\},\, l \neq k} u_{kl}^v, \quad \forall k \in K,\ \forall v \in V_T \tag{C6}$$

### Chaque cluster actif est visité exactement une fois (par l'ensemble des camions)

$$\sum_{v \in V_T} \sum_{l \in K \cup \{0\},\, l \neq k} u_{lk}^v = y_k, \quad \forall k \in K \tag{C7}$$

### Les camions partent et reviennent au dépôt

$$\sum_{l \in K} u_{0l}^v = \sum_{l \in K} u_{l0}^v \leq 1, \quad \forall v \in V_T \tag{C8}$$

### Elimination des sous-tours (MTZ — Miller, Tucker, Zemlin)

$$s_k^v - s_l^v + |K| \cdot u_{kl}^v \leq |K| - 1, \quad \forall k, l \in K,\ k \neq l,\ \forall v \in V_T \tag{C9}$$

$$1 \leq s_k^v \leq |K|, \quad \forall k \in K,\ \forall v \in V_T \tag{C10}$$

### Capacité des camions

$$\sum_{k \in K} y_k \cdot Q_k^{\text{demand}} \cdot u_{0k}^v \leq Q_T, \quad \forall v \in V_T \tag{C11}$$

où $Q_k^{\text{demand}}$ est la demande agrégée estimée du cluster $k$.

---

## 7. Contraintes de Routage — Niveau 2 (Motos, intra-cluster)

Pour chaque cluster $k$ actif, les motos distribuent les colis aux lockers ouverts.

### Conservation de flux dans le cluster

$$\sum_{j' \in J_k,\, j' \neq j} w_{j'j}^v = \sum_{j' \in J_k,\, j' \neq j} w_{jj'}^v, \quad \forall j \in J_k,\ \forall v \in V_M \tag{C12}$$

### Chaque locker ouvert est visité exactement une fois dans son cluster

$$\sum_{v \in V_M} \sum_{j' \in J_k,\, j' \neq j} w_{j'j}^v = x_j, \quad \forall k \in K,\ \forall j \in J_k \tag{C13}$$

### Elimination des sous-tours intra-cluster (MTZ)

$$\sigma_j^v - \sigma_{j'}^v + |J_k| \cdot w_{jj'}^v \leq |J_k| - 1, \quad \forall j, j' \in J_k,\ j \neq j',\ \forall v \in V_M \tag{C14}$$

### Capacité des motos

$$\sum_{j \in J_k} x_j \cdot \text{demand}_j \leq Q_M \quad \text{(par tournée de moto)} \tag{C15}$$

---

## 8. Linéarisation de l'Objectif MNL

L'objectif MNL est **non-linéaire** (somme de fractions). Pour le résoudre avec Gurobi (MILP), on le linéarise.

### 8.1 Substitution de variable

On introduit :

$$z_{ij} = x_j \cdot p_{ij}, \quad \forall i \in I,\ \forall j \in J$$

Le produit d'une binaire $x_j$ et d'une continue $p_{ij}$ se linéarise par les **inégalités de McCormick** :

$$z_{ij} \leq p_{ij} \tag{L1}$$

$$z_{ij} \leq x_j \tag{L2}$$

$$z_{ij} \geq p_{ij} + x_j - 1 \tag{L3}$$

$$z_{ij} \geq 0 \tag{L4}$$

### 8.2 Réécriture de la probabilité MNL

En posant $A_i(\mathbf{x}) = \sum_{j \in J} x_j \cdot a_{ij} + B_c^i$, la probabilité devient :

$$p_{ij} = \frac{x_j \cdot a_{ij}}{A_i(\mathbf{x})} \implies p_{ij} \cdot A_i(\mathbf{x}) = x_j \cdot a_{ij}$$

En remplaçant $x_j \cdot a_{ij}$ par $a_{ij} \cdot z_{ij}$ et en développant $A_i(\mathbf{x})$ :

$$p_{ij} \left(\sum_{j' \in J} a_{ij'} \cdot z_{ij'} + B_c^i \cdot 1\right) = a_{ij} \cdot z_{ij}$$

Cette équation reste bilinéaire. La **reformulation exacte MILP** utilise la variable :

$$\theta_i = \frac{1}{A_i(\mathbf{x})} \quad \Rightarrow \quad p_{ij} = a_{ij} \cdot z_{ij} \cdot \theta_i$$

> En pratique, on peut utiliser la **méthode de Charnes-Cooper** ou les **inégalités de linéarisation conditionnelles** (Lin et al. 2020) pour obtenir un MILP exact. Pour les grandes instances, l'algorithme QT-LA (Quadratic Transform + Linear Alternating) de Lin et al. est recommandé.

### 8.3 Formulation MILP résultante (approche simplifiée)

En fixant $\theta_i$ et en alternant entre les variables de localisation et les variables de part de marché (approche itérative), on obtient à chaque itération un MILP :

$$\max \sum_{i \in I} d_i \sum_{j \in J} a_{ij} \cdot z_{ij} \cdot \theta_i^{(t)}$$

sous les contraintes :

$$\sum_{j \in J} a_{ij} \cdot z_{ij} + B_c^i \cdot \theta_i = 1, \quad \forall i \in I \tag{MNL-1}$$

$$z_{ij} \leq x_j \cdot \theta_i^{\max}, \quad \forall i,j \tag{MNL-2}$$

$$\theta_i \geq 0, \quad z_{ij} \geq 0, \quad x_j \in \{0,1\} \tag{MNL-3}$$

---

## 9. Formulation Complète (Récapitulatif)

$$\boxed{
\begin{aligned}
\max \quad & Z = \sum_{i \in I} d_i \sum_{j \in J} P_{ij}(\mathbf{x}) - \sum_j f_j x_j - C_{\text{routing}} \\[6pt]
\text{s.t.} \quad
& \text{(C1) Budget} \\
& \text{(C2) Nombre de lockers} \\
& \text{(C3) Capacité lockers} \\
& \text{(C4–C5) Activation clusters} \\
& \text{(C6–C11) Routage camions (VRP niveau 1)} \\
& \text{(C12–C15) Routage motos (VRP niveau 2)} \\
& \text{(L1–L4) Linéarisation McCormick} \\
& \text{(MNL-1–3) Reformulation MNL} \\[4pt]
& x_j \in \{0,1\},\ y_k \in \{0,1\},\ u_{kl}^v \in \{0,1\},\ w_{jj'}^v \in \{0,1\} \\
& p_{ij} \geq 0,\ z_{ij} \geq 0,\ s_k^v \geq 0,\ \sigma_j^v \geq 0
\end{aligned}
}$$

---

## 10. Propriétés et Complexité

| Propriété | Valeur |
|---|---|
| Type de problème | MLFP → MILP (après reformulation) |
| Variables binaires | $|J| + |K| + |K|^2 \cdot |V_T| + |J|^2 \cdot |V_M|$ |
| Variables continues | $|I| \cdot |J|$ (parts de marché) + variables MTZ |
| Complexité | NP-difficile (LRP ⊃ TSP) |
| Objectif | Non-linéaire → linéarisé par McCormick |
| Solver cible | **Gurobi** (MILP exact sur petites instances) |

---

## 11. Stratégie de Résolution Recommandée

```
Étape 1 : Résoudre le sous-problème de localisation seul (routing coût fixe)
           → Valider le MNL et la linéarisation

Étape 2 : Résoudre le routage camions seul (clusters fixes)
           → Valider le VRP niveau 1

Étape 3 : Résoudre le routage motos seul (lockers ouverts fixes)
           → Valider le VRP niveau 2

Étape 4 : Coupler les trois sous-problèmes
           → LRP complet, testé sur petite instance (|J|≤20, |K|≤5)

Étape 5 : Passer à l'échelle (|J|~200, |K|~20)
           → Décomposition de Benders ou heuristique de grand voisinage (LNS)
```

---

## 12. Notation Synthétique

| Symbole | Type | Rôle |
|---|---|---|
| $x_j$ | Binaire | Ouvrir locker $j$ |
| $y_k$ | Binaire | Cluster $k$ actif |
| $u_{kl}^v$ | Binaire | Arc camion $k \to l$ |
| $w_{jj'}^v$ | Binaire | Arc moto $j \to j'$ |
| $p_{ij}$ | Continue $[0,1]$ | Part de demande zone $i$ → locker $j$ |
| $z_{ij}$ | Continue $[0,1]$ | Linéarisation $x_j \cdot p_{ij}$ |
| $s_k^v$ | Continue | Position MTZ camion (anti-subtour) |
| $\sigma_j^v$ | Continue | Position MTZ moto (anti-subtour) |
| $a_{ij}$ | Paramètre | Attractivité locker $j$ pour zone $i$ |
| $b_{ic}$ | Paramètre | Attractivité concurrent $c$ pour zone $i$ |
| $B_c^i$ | Paramètre | Attractivité totale fixe pour zone $i$ |

---

*Document de référence — Stage UFMG 2026 — Ricardo Saraiva de Camargo*
