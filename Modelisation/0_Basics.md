# Formulation Mathématique — LRP avec Lockers Stationnaires et MNL

## 1. Indices et Ensembles


### Part de marché capturée

$$
\text{max: }
w_i\sum_{j \in J}
\frac
    {U_{ij} \cdot y_j}
    {\displaystyle\sum_{k \in J} u_{ik} \cdot y_k + \sum_{c \in C} U_{ic}}
$$
$$
w_i​ \rarr \text{demand in zone i}
$$
$$
j \in J​ \rarr \text{index candidates sites}
$$
$$
y_j​ \in \{0,1\} \rarr \text{binary decision, locker open or not}
$$
$$
k \in J​ \rarr \text{same index as j}
$$
$$
c \in C​ \rarr \text{index competitors}
$$
$$
U_ic​ \rarr \text{utility competitors}
$$
$$
u_{ik} \cdot y_k \rarr \text{utility of open lockers}
$$

### Définition de l'utilité U ij​

$$
u_{ik} = \frac
    {A_j}
    {\Rho}
$$
or 
$$
u_{ij} = \frac
    {A_j}
    {d_{ij}^\rho}
$$

$$
A_j \rarr  \text{Attractivité intrinsèque du locker j}
$$
$$
d_{ij} \rarr  \text{​Distance entre la zone i et le site j}
$$
$$
\rho \rarr  \text{Exposant de décroissance (power law) } p=2
$$
---

### Attractivité totale des concurrents

$$
\sum_{c \in C} U_{ic} = u^0
$$

$$
u^0 \rarr \text{Constant representing total attractivity of competitors in area i}
$$

---

### Nombre maximal de lockers

$$
\sum_{j \in J} y_j \le P  \quad | \quad y_j \in \{0,1\} \quad | \quad \forall j \in J
$$

---

### Extension multi-types

$$
\max \sum_{i \in I} w_i \sum_{j \in J} \sum_{e \in E} 
\frac
{u_{ij}^e \cdot y_{je}}
{
    \sum_{k \in J}\sum_{e}
    u_{ik}^e \cdot y_{ke}
    +u^0
}
$$

$$
e \rarr  \text{type of locker}
$$
$$
j, k \rarr  \text{candidate site for locker}
$$
$$
w_i \rarr  \text{population on area i}
$$
$$
u_{ij}^e \rarr  \text{Utility of the locker of type e at the site j for area i}
$$
$$
\sum_{k}\sum_{l} u_{ik}^l \rarr  \text{total attractivity}
$$
---
$$
t\sqrt{n_kA_k} \rarr \text{routing cost}
$$

$$
t \rarr \text{distance factor (t=0.89, euclide distance)}
$$
$$
n_k \rarr \text{nb of customers in the cluster}
$$
$$
A_k \rarr \text{area}
$$