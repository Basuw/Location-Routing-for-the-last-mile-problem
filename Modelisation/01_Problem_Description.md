# Problème de Location-Routing pour les Lockers Intelligents — Minas Gerais

## 1. Vue d'ensemble

L'objectif est de **concevoir un réseau de lockers  stationnaires** dans les zones rurales et sous-desservies de Minas Gerais, afin de **maximiser la part de marché capturée** face à des concurrents existants (Correios, Mercado Livre, etc.).

Le problème mêle deux décisions interdépendantes :

- **Décision de localisation** : quels sites ouvrir comme lockers ?
- **Décision de routage** : comment acheminer les colis jusqu'aux lockers (camions inter-clusters, motos intra-cluster) ?

Le comportement des clients est modélisé par un **modèle de choix probabiliste (Multinomial Logit)** : chaque client choisit un locker avec une probabilité qui dépend de l'attractivité du locker et de sa distance.

---

## 2. Architecture générale du réseau

```mermaid
graph TD
    DEPOT["🏭 Dépôt Central"]

    subgraph Cluster_A["Cluster A (zone géographique)"]
        LA1["📦 Locker A1"]
        LA2["📦 Locker A2"]
        LA3["📦 Locker A3"]
    end

    subgraph Cluster_B["Cluster B"]
        LB1["📦 Locker B1"]
        LB2["📦 Locker B2"]
    end

    subgraph Cluster_C["Cluster C"]
        LC1["📦 Locker C1"]
        LC2["📦 Locker C2"]
        LC3["📦 Locker C3"]
    end

    DEPOT -- "🚛 Camion (inter-cluster)" --> Cluster_A
    DEPOT -- "🚛 Camion (inter-cluster)" --> Cluster_B
    DEPOT -- "🚛 Camion (inter-cluster)" --> Cluster_C

    Cluster_A -- "🚛 Camion (connectivité clusters)" --> Cluster_B
    Cluster_B -- "🚛 Camion (connectivité clusters)" --> Cluster_C

    LA1 -- "🏍️ Moto (intra-cluster)" --> LA2
    LA2 -- "🏍️ Moto (intra-cluster)" --> LA3

    LB1 -- "🏍️ Moto" --> LB2

    LC1 -- "🏍️ Moto" --> LC2
    LC2 -- "🏍️ Moto" --> LC3
```

> **Lecture du schéma :** Les camions partent du dépôt et relient les clusters entre eux (niveau 1). Au sein de chaque cluster, des motos distribuent les colis aux lockers individuels (niveau 2). Les clients se rendent ensuite au locker de leur choix.

---

## 3. Les acteurs du système

### 3.1 Les camions 🚛

```mermaid
graph LR
    D["🏭 Dépôt"] -->|"Route camion"| CA["Hub Cluster A"]
    CA -->|"Route camion"| CB["Hub Cluster B"]
    CB -->|"Route camion"| CC["Hub Cluster C"]
    CC -->|"Retour"| D

    style D fill:#2c3e50,color:#fff
    style CA fill:#e67e22,color:#fff
    style CB fill:#e67e22,color:#fff
    style CC fill:#e67e22,color:#fff
```

- **Rôle** : transport en gros volume entre le dépôt et les hubs de chaque cluster
- **Contraintes** : capacité de chargement, durée maximale de tournée, coût kilométrique
- **Décision** : quels clusters visiter et dans quel ordre (VRP niveau 1)

### 3.2 Les motos 🏍️

```mermaid
graph LR
    HUB["📍 Hub du Cluster"] -->|"Livraison"| L1["📦 Locker 1"]
    L1 -->|"Livraison"| L2["📦 Locker 2"]
    L2 -->|"Livraison"| L3["📦 Locker 3"]
    L3 -->|"Retour"| HUB

    style HUB fill:#8e44ad,color:#fff
    style L1 fill:#27ae60,color:#fff
    style L2 fill:#27ae60,color:#fff
    style L3 fill:#27ae60,color:#fff
```

- **Rôle** : distribution fine à l'intérieur d'un cluster, entre le hub et chaque locker ouvert
- **Avantage** : accès aux zones difficiles, routes étroites, zones rurales
- **Contraintes** : capacité limitée (quelques colis), rayon d'action
- **Décision** : quels lockers visiter et dans quel ordre (VRP niveau 2)

### 3.3 Les clients 🧑‍🤝‍🧑

```mermaid
graph TD
    C1["👤 Client zone 1"] -->|"Choix probabiliste"| L_OPT["📦 Locker choisi"]
    C2["👤 Client zone 2"] -->|"Choix probabiliste"| L_OPT
    C3["👤 Client zone 3"] -->|"Choix probabiliste"| COMP["🏪 Concurrent"]
    C4["👤 Client zone 4"] -->|"Aucun service"| NONE["❌ Non servi"]

    style L_OPT fill:#27ae60,color:#fff
    style COMP fill:#e74c3c,color:#fff
    style NONE fill:#95a5a6,color:#fff
```

- **Rôle** : ils se déplacent d'eux-mêmes vers un locker (ou un concurrent)
- **Modèle** : leur choix est probabiliste — modélisé par le **Multinomial Logit (MNL)**
- **Facteurs** : distance au locker, attractivité du locker, attractivité des concurrents

---

## 4. Le modèle d'attraction des clients (MNL)

### Intuition

Chaque client dans une zone $i$ fait face à plusieurs alternatives :
- Les lockers ouverts par l'opérateur $\{j \in J : x_j = 1\}$
- Les lockers des concurrents $\{c \in C\}$
- L'option "ne pas utiliser de locker" (option extérieure)

Le client choisit l'option qui maximise son utilité perçue, avec une composante aléatoire.

```mermaid
graph TD
    CLIENT["👤 Client en zone i"]

    subgraph Nos_lockers["Nos lockers (ouverts)"]
        J1["📦 Locker j1\nAttrait: a_i1"]
        J2["📦 Locker j2\nAttrait: a_i2"]
    end

    subgraph Concurrents["Concurrents (fixes)"]
        C1["🏪 Concurrent c1\nAttrait: b_i1"]
        C2["🏪 Concurrent c2\nAttrait: b_i2"]
    end

    NONE["❌ Option extérieure\nAttrait: a_i0"]

    CLIENT -->|"Prob P_ij1"| J1
    CLIENT -->|"Prob P_ij2"| J2
    CLIENT -->|"Prob Q_ic1"| C1
    CLIENT -->|"Prob Q_ic2"| C2
    CLIENT -->|"Prob P_i0"| NONE

    style J1 fill:#27ae60,color:#fff
    style J2 fill:#27ae60,color:#fff
    style C1 fill:#e74c3c,color:#fff
    style C2 fill:#e74c3c,color:#fff
    style NONE fill:#95a5a6,color:#fff
```

### Attractivité décroissante avec la distance

L'attractivité d'un locker $j$ pour un client en zone $i$ décroît avec la distance $d_{ij}$ :

```
Attractivité
    │
  1 │ ●
    │    ●
    │        ●
    │            ●
  0 │                ●  ●  ●  ●  ● ─────────
    └──────────────────────────────────────── Distance d_ij
         proche            loin
```

Formule : $a_{ij} = e^{\,\alpha_j - \beta \cdot d_{ij}}$

- $\alpha_j$ : attractivité intrinsèque du locker $j$ (taille, équipements, réputation)
- $\beta$ : sensibilité des clients à la distance (paramètre à calibrer)
- Plus $\beta$ est grand, plus les clients sont "sensibles" à la distance

---

## 5. Structure en clusters géographiques

### Pourquoi des clusters ?

Dans les zones rurales de MG, les ~20 000 points de livraison ne peuvent pas être servis un par un par des camions. On **agrège les sites** en zones géographiques cohérentes (municípios, bassins de population, etc.) appelées **clusters**.

```mermaid
graph TD
    subgraph MG["État de Minas Gerais"]
        subgraph KA["Cluster A\n(Nord-Ouest MG)"]
            A1[📦] --- A2[📦]
            A2 --- A3[📦]
        end
        subgraph KB["Cluster B\n(Centre MG)"]
            B1[📦] --- B2[📦]
        end
        subgraph KC["Cluster C\n(Sud MG)"]
            C1[📦] --- C2[📦]
            C2 --- C3[📦]
        end
        subgraph KD["Cluster D\n(Est MG)"]
            D1[📦]
        end

        KA <-->|"Route camion"| KB
        KB <-->|"Route camion"| KC
        KB <-->|"Route camion"| KD
    end
```

### Règles de connectivité des clusters

- Chaque cluster ouvert (possédant au moins un locker) **doit être relié** au réseau de distribution
- La connectivité est assurée par les routes de camions
- Les clusters forment un **graphe connexe** dans la solution finale
- Un cluster non connecté = ses lockers ne peuvent pas être réapprovisionnés = solution infaisable

```mermaid
graph LR
    D["🏭 Dépôt"]
    KA["Cluster A"] 
    KB["Cluster B"]
    KC["Cluster C"]

    D --> KA
    KA --> KB
    KB --> KC
    KC --> D

    style D fill:#2c3e50,color:#fff
    style KA fill:#e67e22,color:#fff
    style KB fill:#e67e22,color:#fff
    style KC fill:#e67e22,color:#fff
```

> La tournée des camions forme un **cycle** passant par tous les clusters ouverts et revenant au dépôt (structure VRP/TSP au niveau cluster).

---

## 6. Les concurrents

```mermaid
graph TD
    MARKET["🎯 Marché total\n(demande totale de MG)"]

    OUR["Notre réseau\nde lockers"]
    COMP["Concurrents\n(Correios, ML, Amazon...)"]
    NONE["Non capturée\n(pas de service)"]

    MARKET -->|"Part capturée"| OUR
    MARKET -->|"Part capturée"| COMP
    MARKET -->|"Reste"| NONE

    style OUR fill:#27ae60,color:#fff
    style COMP fill:#e74c3c,color:#fff
    style NONE fill:#95a5a6,color:#fff
```

- Les concurrents ont des **lockers/agences déjà en place** → leurs attractivités $b_{ic}$ sont **fixées** (données exogènes)
- Notre opérateur **ne contrôle pas** les décisions des concurrents
- L'objectif est de maximiser notre part du marché en choisissant stratégiquement où ouvrir nos lockers

---

## 7. Résumé des décisions du problème

| Décision | Type | Description |
|---|---|---|
| Ouvrir le locker $j$ ? | Binaire $x_j \in \{0,1\}$ | Localisation |
| Route des camions | Entier (arcs) | Routage niveau 1 (inter-cluster) |
| Route des motos | Entier (arcs) | Routage niveau 2 (intra-cluster) |
| Clusters connectés ? | Contrainte | Connectivité du réseau |

**Objectif :** Maximiser la part de marché capturée (MNL), sous contrainte de budget et de capacité des véhicules.

---

## 8. Difficulté du problème

```mermaid
graph TD
    LRP["Location-Routing Problem\n(LRP)"]
    LOC["Facility Location\nNP-difficile"]
    VRP["Vehicle Routing Problem\nNP-difficile"]
    MNL_FRAC["Objectif MNL\n(fraction non-linéaire)"]
    HIER["Routage hiérarchique\n(2 niveaux)"]

    LRP --> LOC
    LRP --> VRP
    LRP --> MNL_FRAC
    LRP --> HIER

    style LRP fill:#c0392b,color:#fff
    style LOC fill:#e74c3c,color:#fff
    style VRP fill:#e74c3c,color:#fff
    style MNL_FRAC fill:#e74c3c,color:#fff
    style HIER fill:#e74c3c,color:#fff
```

Le LRP est **NP-difficile** en lui-même. L'ajout du MNL (objectif fractionnaire non-linéaire) et du routage à deux niveaux en font un problème très complexe. La stratégie de résolution repose sur :

1. **Linéarisation** du MNL (reformulation McCormick)
2. **Décomposition hiérarchique** (résoudre localisation puis routage, ou Benders)
3. **Instances réduites** pour validation, puis passage à l'échelle

---

*Document de référence — Stage UFMG 2026 — Bastien Jacquelin*
