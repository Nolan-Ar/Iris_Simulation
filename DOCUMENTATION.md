# IRIS - Documentation Technique Complète

## Table des matières

1. [Introduction](#1-introduction)
2. [Architecture globale](#2-architecture-globale)
3. [Concepts fondamentaux](#3-concepts-fondamentaux)
4. [Le RAD - Régulateur Automatique Décentralisé](#4-le-rad---régulateur-automatique-décentralisé)
5. [Les composants du système](#5-les-composants-du-système)
6. [Algorithmes de régulation](#6-algorithmes-de-régulation)
7. [Flux économiques](#7-flux-économiques)
8. [Démographie et dynamique de population](#8-démographie-et-dynamique-de-population)
9. [Chambre de Relance](#9-chambre-de-relance)
10. [Formules mathématiques complètes](#10-formules-mathématiques-complètes)
11. [Guide d'utilisation avancé](#11-guide-dutilisation-avancé)
12. [Dépannage et FAQ](#12-dépannage-et-faq)

---

## 1. Introduction

### 1.1 Qu'est-ce qu'IRIS ?

**IRIS** (Integrative Resilience Intelligence System) est un système économique expérimental qui simule une économie complète avec régulation automatique basée sur des principes thermodynamiques.

Le système est conçu pour maintenir un **équilibre thermodynamique** entre la valeur productive (V) et la dette thermométrique (D) via un régulateur automatique appelé **RAD**.

### 1.2 Principes directeurs

1. **Conservation thermodynamique** : `V₀ = D₀` (équilibre initial parfait)
2. **Pas de création ex nihilo** : Toute valeur créée a une contrepartie
3. **Régulation automatique** : Système cybernétique sans intervention humaine
4. **Décentralisation** : Chaque agent agit de manière autonome
5. **Résilience** : Le système s'adapte automatiquement aux perturbations

### 1.3 Échelle temporelle

- **1 step = 1 mois** (fixe, non modifiable)
- **12 steps = 1 an** (STEPS_PER_YEAR = 12)
- Les simulations typiques durent 60-120 cycles (5-10 ans)

---

## 2. Architecture globale

### 2.1 Structure du projet

```
Iris_Simulation/
│
├── iris/                           # Package principal
│   ├── core/                       # Composants cœur du système
│   │   ├── iris_model.py          # IRISEconomy - Modèle principal
│   │   ├── iris_rad.py            # RADState - Régulateur automatique
│   │   ├── iris_types.py          # Types de données (Agent, Asset, etc.)
│   │   ├── iris_demographics.py   # Démographie (naissances, décès)
│   │   ├── iris_catastrophes.py   # Événements catastrophiques
│   │   ├── iris_chambre_relance.py # Chambre de Relance
│   │   └── __init__.py            # Exports publics
│   │
│   ├── utils/                      # Utilitaires
│   │   └── helpers.py             # Fonctions utilitaires
│   │
│   └── __init__.py
│
├── tests/                          # Tests (à développer)
│   └── test_antagonism.py         # Test de l'antagonisme κ/η
│
├── requirements.txt                # Dépendances Python
├── README.md                       # Documentation utilisateur
├── DOCUMENTATION.md               # Ce fichier
└── Iris_proto_complet.md          # Spécifications théoriques

```

### 2.2 Diagramme de flux

```
┌─────────────────────────────────────────────────────────────┐
│                      IRISEconomy                            │
│  (Modèle économique principal)                              │
│                                                              │
│  ┌────────────┐  ┌──────────────┐  ┌───────────────┐       │
│  │  Agents    │  │  Assets      │  │  Businesses   │       │
│  │  (V, U)    │  │  (D_*)       │  │  (S)          │       │
│  └────────────┘  └──────────────┘  └───────────────┘       │
│         │                │                  │                │
│         └────────────────┼──────────────────┘                │
│                          ▼                                   │
│                   ┌─────────────┐                            │
│                   │    RAD      │ ◄────────┐                 │
│                   │ (θ, κ, η)   │          │                 │
│                   └─────────────┘          │                 │
│                          │                 │                 │
│         ┌────────────────┼─────────────────┤                 │
│         ▼                ▼                 ▼                 │
│  ┌────────────┐  ┌──────────────┐  ┌─────────────┐          │
│  │Demographics│  │Catastrophes  │  │  Chambre    │          │
│  │            │  │              │  │  Relance    │          │
│  └────────────┘  └──────────────┘  └─────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Concepts fondamentaux

### 3.1 Les quatre monnaies

#### 3.1.1 V (Valeur vivante)

- **Définition** : Valeur productive en circulation, attachée aux actifs réels
- **Nature** : Stock d'épargne, patrimoine des agents
- **Propriétés** :
  - Amortie via D (δₘ ≈ 1.25%/an)
  - Convertible en U via κ
  - Créée par combustion S+U

#### 3.1.2 U (Revenu Universel)

- **Définition** : Monnaie de flux, distribuée périodiquement
- **Nature** : Revenus courants des agents
- **Propriétés** :
  - Distribué mensuellement : `U_i = (1-ρ) × V_on / (12 × N)`
  - Éteint annuellement (fin d'année)
  - Utilisable pour combustion (S+U→V)
  - Convertible depuis V via κ

#### 3.1.3 S (Stipulat)

- **Définition** : Crédit productif pour les entreprises
- **Nature** : Financement entrepreneurial
- **Propriétés** :
  - Créé avec les nouvelles entreprises
  - Combustible avec U pour créer V
  - Poids w_S dans la combustion

#### 3.1.4 D (Dette thermométrique)

- **Définition** : Miroir de la valeur pour la régulation
- **Nature** : Indicateur thermodynamique (PAS une dette juridique)
- **Propriétés** :
  - 5 composantes (D_materielle, D_services, D_contractuelle, D_engagement, D_regulatrice)
  - Utilisée pour calculer θ = D/V_on
  - Amortie mensuellement (δₘ ≈ 0.104%/mois)

### 3.2 Les 5 composantes de D

```
D_total = D_materielle + D_services + D_contractuelle + D_engagement + D_regulatrice
```

| Composante | Description | Origine |
|------------|-------------|---------|
| **D_materielle** | Biens et immobilisations physiques | Actifs IMMOBILIER, MOBILIER |
| **D_services** | Flux d'entretien et maintenance | Actifs SERVICE |
| **D_contractuelle** | Titres à promesse productive | Actifs ENTREPRISE (NFT financiers) |
| **D_engagement** | Staking et mises en réserve | Future implémentation TAP/Staking |
| **D_regulatrice** | Chambre de Relance | RU, redistribution, ajustements C3 |

### 3.3 Le thermomètre θ

```
θ = D / V_on
```

Où `V_on` est la **valeur vivante** (actifs non-orphelins en possession des agents).

**Interprétation** :

- **θ < 1** : Sous-investissement (D insuffisant par rapport à V)
  - Économie en léthargie
  - RAD stimule : κ↑, η↑

- **θ = 1** : Équilibre parfait (CIBLE)
  - État optimal du système
  - RAD maintient l'équilibre

- **θ > 1** : Surchauffe (D excessif par rapport à V)
  - Économie en surchauffe
  - RAD freine : κ↓, η↓

### 3.4 L'indicateur I

```
I = θ - 1
```

Mesure l'écart à l'équilibre :
- `|I| < 0.15` : Régulation normale (C1 uniquement)
- `0.15 < |I| < 0.30` : Activation C2 (régulation profonde)
- `|I| > 0.30` : Activation C3 (crise, intervention d'urgence)

---

## 4. Le RAD - Régulateur Automatique Décentralisé

### 4.1 Qu'est-ce que le RAD ?

Le **RAD** est le "thermostat" de l'économie IRIS. C'est un régulateur automatique qui ajuste en continu les paramètres économiques pour maintenir `θ = 1`.

**Analogie thermodynamique** :
- Thermomètre → θ
- Thermostat → RAD
- Température cible → θ = 1
- Leviers de régulation → κ, η, D_regulatrice

### 4.2 Architecture multi-couches

Le RAD opère sur **3 couches complémentaires** :

#### Couche 1 (C1) - Régulation continue

**Fréquence** : Chaque cycle (mensuelle)

**Actions** :
1. Calcul des 3 capteurs (r_t, ν_eff, τ_eng)
2. Ajustement κ et η via algorithme antagoniste
3. (Amortissement D déplacé dans step() pour éviter double application)

**Caractéristiques** :
- Rétroaction négative instantanée
- Ajustements fins et progressifs
- Contraintes : |Δκ|, |Δη| ≤ 0.15 (15% max/cycle)

#### Couche 2 (C2) - Régulation profonde

**Fréquence** : Tous les 12 cycles (annuelle)

**Condition d'activation** : `|I| > 0.15`

**Actions** :
- Recalibrage structurel (actuellement minimal)
- Possibilité d'ajuster les paramètres α, β, γ
- Adaptation long terme

#### Couche 3 (C3) - Rebalancement d'urgence

**Condition d'activation** : `|I| > 0.30`

**Actions** :
1. Calcul de l'ajustement : `adjustment = (V_on - D) × 0.1`
2. Application progressive sur D_regulatrice
3. Limite : max 5 cycles consécutifs
4. Cooldown : 5 cycles de repos après intervention

**Caractéristiques** :
- Mécanisme de dernier recours
- Intervention directe sur D
- Évite les divergences critiques

### 4.3 Système tri-capteur

Le RAD utilise **3 capteurs** pour mesurer l'état de l'économie :

#### Capteur 1 : r_t (Thermomètre)

```
r_t = θ = D / V_on
```

- **Cible** : 1.0
- **Mesure** : Équilibre thermodynamique global
- **Rôle** : Indicateur principal de surchauffe/sous-régime

#### Capteur 2 : ν_eff (Vélocité effective)

```
ν_eff = (U_burn + S_burn) / V_on_previous
```

- **Cible** : 0.20 (20%)
- **Mesure** : Vigueur de l'activité économique réelle
- **Rôle** : Détecte léthargie ou hyperactivité

#### Capteur 3 : τ_eng (Taux d'engagement)

```
τ_eng = U_stake / U_total
```

- **Cible** : 0.35 (35%)
- **Mesure** : Part de U engagée en staking
- **Rôle** : Indicateur social (sacrifice du présent pour le futur)

### 4.4 Les coefficients de régulation

#### κ (kappa) - Coefficient de liquidité

**Rôle** : Régule la conversion V → U

```python
U_converted = kappa × V_amount
```

- **Neutre** : κ = 1.0 (conversion 1:1)
- **Bornes** : [0.5, 2.0]
- **Effet** :
  - κ > 1 : Facilite conversion V→U (stimulation)
  - κ < 1 : Freine conversion V→U (refroidissement)

#### η (eta) - Rendement de combustion

**Rôle** : Régule l'efficacité S+U → V

```python
V_created = eta × sqrt(w_S × S² + w_U × U²)
```

- **Neutre** : η = 1.0 (rendement normal)
- **Bornes** : [0.5, 2.0]
- **Effet** :
  - η > 1 : Augmente création de V (stimulation)
  - η < 1 : Diminue création de V (refroidissement)

### 4.5 Tracking des flux

Le RAD maintient des compteurs pour calculer les capteurs :

```python
# Mis à jour pendant le cycle
U_burn: float = 0.0      # U brûlé (combustion)
S_burn: float = 0.0      # S brûlé (combustion)
U_stake: float = 0.0     # U mis en staking
U_total: float = 0.0     # U total en circulation
V_on_previous: float = 0.0  # V_on du cycle précédent
```

Ces valeurs sont **réinitialisées** au début de chaque cycle et accumulées pendant les opérations.

---

## 5. Les composants du système

### 5.1 IRISEconomy (iris_model.py)

**Classe principale** qui orchestre toute la simulation.

#### Attributs principaux

```python
agents: Dict[str, Agent]           # Dictionnaire des agents
assets: Dict[str, Asset]           # Dictionnaire des actifs
businesses: Dict[str, Business]    # Dictionnaire des entreprises
rad: RADState                      # Instance du RAD
demographics: Demographics         # Gestionnaire de population
catastrophes: CatastropheManager   # Gestionnaire d'événements
chambre_relance: ChambreRelance    # Chambre de Relance
time: int                          # Temps actuel (en mois)
```

#### Méthodes principales

```python
step()                    # Avance la simulation d'un cycle
regulate()                # Applique la régulation RAD (C1/C2/C3)
thermometer() -> float    # Calcule θ = D/V_on
indicator() -> float      # Calcule I = θ - 1
get_V_on() -> float       # Calcule V vivante (non-orpheline)
distribute_universal_income()  # Distribue le RU mensuel
```

### 5.2 RADState (iris_rad.py)

**Classe de régulation** qui maintient l'état du RAD.

#### Méthodes de régulation

```python
# Système tri-capteur
update_sensors(theta, total_U, V_on)
calculate_nu_eff(U_burn, S_burn, V_on_prev) -> float
calculate_tau_eng(U_stake, U_total) -> float

# Régulation antagoniste (NOUVELLE)
update_kappa_eta_antagonist(theta, nu_eff, tau_eng)

# Anciennes méthodes (dépréciées, mais conservées)
update_kappa(r_t, nu_eff, tau_eng)
update_eta(r_t, nu_eff, tau_eng)

# Gestion de D
apply_amortization(time_scale="months") -> float
total_D() -> float

# Statistiques
get_statistics() -> Dict[str, Any]
auto_calibrate(time: int) -> Dict[str, Any]
```

### 5.3 Agent (iris_types.py)

**Représente** un agent économique individuel.

```python
@dataclass
class Agent:
    id: str                          # Identifiant unique
    V_balance: float = 0.0           # Solde V (valeur vivante)
    U_balance: float = 0.0           # Solde U (revenu universel)
    assets: List[Asset] = []         # Liste des actifs possédés
    contribution_score: float = 0.0  # Score de contribution
    consumables: float = 0.0         # Biens de consommation accumulés
```

### 5.4 Asset (iris_types.py)

**Représente** un actif économique.

```python
@dataclass
class Asset:
    id: str                          # Identifiant unique
    asset_type: AssetType            # Type (IMMOBILIER, MOBILIER, etc.)
    owner_id: Optional[str]          # Propriétaire actuel
    V_initial: float                 # Valeur V à la création
    D_initial: float                 # Dette D à la création
    creation_time: int               # Temps de création
    last_maintenance: int = 0        # Dernier entretien
    physical_state: float = 1.0      # État physique [0, 1]
```

#### Types d'actifs (AssetType)

```python
class AssetType(Enum):
    IMMOBILIER = "immobilier"      # → D_materielle
    MOBILIER = "mobilier"          # → D_materielle
    SERVICE = "service"            # → D_services
    ENTREPRISE = "entreprise"      # → D_contractuelle
```

### 5.5 Demographics (iris_demographics.py)

**Gère** la dynamique de population.

#### Fonctionnalités

- **Naissances** : Taux de natalité configurable
- **Décès** : Selon espérance de vie (table de mortalité)
- **Héritage** : Transfert patrimoine aux héritiers
- **Dotation initiale** : Nouveaux-nés reçoivent V₀ et actifs

#### Modes de fonctionnement

1. **Mode "object"** : Agents individuels (flexibilité)
2. **Mode "vectorized"** : Arrays NumPy (performance)

### 5.6 CatastropheManager (iris_catastrophes.py)

**Gère** les événements catastrophiques aléatoires.

#### Types de catastrophes

- **Naturelles** : Inondations, tremblements de terre
- **Économiques** : Crises, effondrements sectoriels
- **Sanitaires** : Épidémies, pandémies

#### Effets

- Destruction d'actifs (→ D diminue)
- Mortalité accrue
- Chocs économiques

### 5.7 ChambreRelance (iris_chambre_relance.py)

**Recycle** les actifs orphelins et redistribue la valeur.

#### Raisons d'orphelinage (OrphanReason)

```python
class OrphanReason(Enum):
    DECES_SANS_HERITIER      # Décès sans héritier
    ABANDON_ECONOMIQUE       # Abandon par l'agent
    CATASTROPHE              # Destruction par catastrophe
    FAILLITE                 # Faillite d'entreprise
```

#### Processus

1. **Réception** : Actifs orphelins arrivent avec métadonnées
2. **Évaluation** : Calcul de la valeur récupérable
3. **Redistribution** : Via RU ou vente aux agents
4. **Tracking** : Statistiques sur les actifs traités

---

## 6. Algorithmes de régulation

### 6.1 Algorithme antagoniste κ/η

**Objectif** : Créer une dynamique différenciée entre κ et η pour simuler l'antagonisme TAP/Staking.

#### Étape 1 : Calcul des variations brutes

```python
# Variation κ (tri-capteur)
Δκ = α_κ × (ν_target - ν_eff)      # Effet vitesse
   - β_κ × (τ_eng - τ_target)      # Effet engagement
   + γ_κ × (1 - θ)                 # Effet thermomètre

# Variation η (tri-capteur)
Δη = α_η × (1 - θ)                 # Effet thermomètre
   + β_η × (ν_target - ν_eff)      # Effet vitesse
   - γ_η × (τ_eng - τ_target)      # Effet engagement
```

#### Étape 2 : Application de l'antagonisme

```python
# Si κ et η vont dans le MÊME sens
if sign(Δκ) == sign(Δη):
    # Atténuer η proportionnellement à |Δκ|
    antagonism_factor = 0.3  # 30% d'atténuation
    eta_attenuation = 1.0 - antagonism_factor × |Δκ|
    eta_attenuation = max(0.3, eta_attenuation)  # Min 30%

    Δη ← Δη × eta_attenuation
```

**Résultat** : κ varie **plus** que η, créant un déséquilibre contrôlé.

#### Étape 3 : Application des contraintes

```python
# Limite variation à ±15%
Δκ = clip(Δκ, -0.15, +0.15)
Δη = clip(Δη, -0.15, +0.15)

# Application
κ ← κ + Δκ
η ← η + Δη

# Bornes [0.5, 2.0]
κ = clip(κ, 0.5, 2.0)
η = clip(η, 0.5, 2.0)
```

### 6.2 Coefficients du tri-capteur

**Pour Δκ** (α_κ, β_κ, γ_κ) :
```python
alpha_kappa = 0.4  # Poids vitesse (fort)
beta_kappa  = 0.3  # Poids engagement (modéré)
gamma_kappa = 0.2  # Poids thermomètre (faible)
```

**Pour Δη** (α_η, β_η, γ_η) :
```python
alpha_eta = 0.3  # Poids thermomètre (modéré)
beta_eta  = 0.4  # Poids vitesse (fort)
gamma_eta = 0.2  # Poids engagement (faible)
```

**Justification** :
- **Vitesse** (β) : Indicateur le plus fiable de l'activité réelle
- **Thermomètre** (α) : Indicateur global mais moins réactif
- **Engagement** (γ) : Indicateur social secondaire

### 6.3 Amortissement de D

**Formule mensuelle** :
```python
δ_m = 0.001041666  # ≈ 0.104% par mois
                   # ≈ 1.25% par an

D_materielle    ← D_materielle    × (1 - δ_m)
D_services      ← D_services      × (1 - δ_m)
D_contractuelle ← D_contractuelle × (1 - δ_m)
D_engagement    ← D_engagement    × (1 - δ_m)
D_regulatrice   ← D_regulatrice   × (1 - δ_m)
```

**Appliqué** : Une seule fois par cycle, à la fin de `step()`.

**Note** : L'amortissement était auparavant appliqué deux fois par cycle (bug corrigé).

---

## 7. Flux économiques

### 7.1 Distribution du Revenu Universel

**Fréquence** : Mensuelle (chaque cycle)

**Formule** :
```python
ρ = conservation_rate  # Taux de conservation (0 ≤ ρ ≤ 0.3)
T = 12                 # Mois par an
N = len(agents)        # Nombre d'agents
V_on = get_V_on()      # Valeur vivante

U_i = (1 - ρ) × V_on / (T × N)
```

**Explication** :
- `(1 - ρ) × V_on` : Part de V disponible pour RU (après conservation)
- Division par `T × N` : Répartition égale mensuelle

**Effet** : Chaque agent reçoit le même montant U, indépendamment de son patrimoine.

### 7.2 Conversion V → U

**Déclencheur** : Agent décide de liquider une partie de son épargne

**Formule** :
```python
U_obtained = κ × V_amount

# Mise à jour
agent.V_balance -= V_amount
agent.U_balance += U_obtained
```

**Effet de κ** :
- `κ > 1` : Bonus à la conversion (stimulation économique)
- `κ < 1` : Pénalité à la conversion (freinage économique)

### 7.3 Combustion S+U → V

**Déclencheur** : Entreprise combine Stipulat (S) et U pour créer de la valeur

**Formule (norme euclidienne pondérée)** :
```python
w_S = 0.5  # Poids Stipulat
w_U = 0.5  # Poids U

V_created = η × sqrt(w_S × S² + w_U × U²)

# Conservation thermodynamique
D_created = V_created
```

**Effet de η** :
- `η > 1` : Rendement supérieur (stimulation production)
- `η < 1` : Rendement inférieur (freinage production)

**Tracking** :
```python
rad.U_burn += U_amount
rad.S_burn += S_amount
```

### 7.4 Extinction annuelle de U

**Fréquence** : Tous les 12 cycles (fin d'année)

**Mécanisme** :
```python
if time % 12 == 0:
    for agent in agents:
        agent.U_balance = 0.0
```

**Justification** : U est une monnaie de **flux**, pas de **stock**. L'extinction empêche l'accumulation et force la circulation.

---

## 8. Démographie et dynamique de population

### 8.1 Structure démographique

#### Âges des agents

```python
agent_ages: Dict[str, int]  # Clé: agent_id, Valeur: âge en mois
```

Chaque cycle :
```python
for agent_id in agent_ages:
    agent_ages[agent_id] += 1
```

#### Espérance de vie

Par défaut : **80 ans** (960 mois)

Table de mortalité utilisée pour probabilités de décès variables selon l'âge.

### 8.2 Naissances

**Taux** : Configurable (défaut : compatible avec stabilité démographique)

**Processus** :
1. Tirage aléatoire selon taux de natalité
2. Création nouvel agent avec :
   - `V_balance` = dotation initiale
   - `U_balance` = 0
   - `assets` = liste d'actifs initiaux
3. Création de D correspondant aux actifs (V₀ = D₀)
4. Ajout au système avec `age = 0`

**Conservation thermodynamique** : Les nouveaux-nés ne créent PAS de valeur ex nihilo. Leur dotation provient de la redistribution du système.

### 8.3 Décès

**Processus** :
1. Vérification probabilité décès selon âge
2. Si décès :
   - Calcul D_lifetime (amortissement lié à l'âge)
   - Transfert patrimoine à héritier (ou Chambre de Relance)
   - Envoi actifs orphelins à Chambre de Relance
   - Suppression agent du système

#### Héritage

**Règle** : Héritier choisi aléatoirement parmi les agents vivants

**Transfert** :
```python
heir.V_balance += deceased.V_balance
heir.U_balance += deceased.U_balance

for asset in deceased.assets:
    asset.owner_id = heir.id
    heir.assets.append(asset)
```

**Cas particulier** : Si aucun héritier disponible → actifs vers Chambre de Relance

### 8.4 Dynamique de population

**Modes** :

1. **"object"** (par défaut) :
   - Agents individuels (objets Agent)
   - Flexibilité maximale
   - Performance : O(N)

2. **"vectorized"** :
   - Arrays NumPy
   - Performance : O(1) pour opérations vectorisées
   - Utilisé pour grandes populations (> 10k agents)

---

## 9. Chambre de Relance

### 9.1 Rôle

La **Chambre de Relance** est un mécanisme de redistribution qui :

1. **Collecte** les actifs orphelins (sans propriétaire)
2. **Évalue** leur valeur récupérable
3. **Redistribue** via RU ou vente aux agents
4. **Maintient** D_regulatrice pour la régulation C3

### 9.2 Cycle de vie d'un actif orphelin

```
┌─────────────┐
│   Événement │ (Décès, Catastrophe, Faillite)
└──────┬──────┘
       │
       ▼
┌────────────────────────────┐
│  add_orphan_asset()        │
│  - Métadonnées             │
│  - Raison d'orphelinage    │
│  - Timestamp               │
└────────┬───────────────────┘
         │
         ▼
┌────────────────────────────┐
│  Évaluation                │
│  - État physique           │
│  - Âge de l'actif          │
│  - Type d'actif            │
└────────┬───────────────────┘
         │
         ▼
┌────────────────────────────┐
│  Redistribution            │
│  - Via RU (D_regulatrice)  │
│  - Ou vente aux agents     │
└────────────────────────────┘
```

### 9.3 Métadonnées orphelines

```python
@dataclass
class OrphanAsset:
    asset_id: str
    asset_type: str
    V_initial: float
    D_initial: float
    reason: OrphanReason
    timestamp_orphelin: int
    age_asset: int
    etat_physique: float
```

### 9.4 Statistiques

```python
chambre_relance.get_statistics() -> {
    "total_orphans_received": int,
    "total_V_recycled": float,
    "total_D_recycled": float,
    "orphans_by_reason": Dict[OrphanReason, int],
    "current_orphans": int
}
```

---

## 10. Formules mathématiques complètes

### 10.1 Régulation κ

```
Δκ_t = α_κ × (ν_target - ν_t-1)
     - β_κ × (τ_eng,t-1 - τ_target)
     + γ_κ × (1 - r_t-1)

Avec :
  α_κ = 0.4
  β_κ = 0.3
  γ_κ = 0.2

Contraintes :
  |Δκ| ≤ 0.15
  κ ∈ [0.5, 2.0]
```

### 10.2 Régulation η

```
Δη_t = α_η × (1 - r_t-1)
     + β_η × (ν_target - ν_t-1)
     - γ_η × (τ_eng,t-1 - τ_target)

Avec :
  α_η = 0.3
  β_η = 0.4
  γ_η = 0.2

Antagonisme :
  Si sign(Δκ) = sign(Δη) :
    Δη ← Δη × (1 - 0.3 × |Δκ|)

Contraintes :
  |Δη| ≤ 0.15
  η ∈ [0.5, 2.0]
```

### 10.3 Capteurs

```
r_t = θ = D / V_on

ν_eff = (U_burn + S_burn) / V_on,t-1

τ_eng = U_stake / U_total
```

### 10.4 Revenu Universel

```
U_i,t = (1 - ρ) × V_on,t / (12 × N_t)

Avec :
  ρ : taux de conservation (0 ≤ ρ ≤ 0.3)
  N_t : nombre d'agents au temps t
  V_on,t : valeur vivante au temps t
```

### 10.5 Combustion

```
V_created = η × sqrt(w_S × S² + w_U × U²)

Avec :
  w_S = 0.5 (poids Stipulat)
  w_U = 0.5 (poids U)

Conservation :
  D_created = V_created
```

### 10.6 Amortissement D

```
D_t+1 = D_t × (1 - δ_m)

Avec :
  δ_m = 0.001041666 ≈ 0.104% / mois
      = 0.0125 / 12 ≈ 1.25% / an
```

### 10.7 Conversion V→U

```
U_obtained = κ × V_converted

agent.V -= V_converted
agent.U += U_obtained
```

---

## 11. Guide d'utilisation avancé

### 11.1 Création d'une simulation personnalisée

```python
from iris.core import IRISEconomy

# Configuration complète
model = IRISEconomy(
    # Population
    initial_agents=100,
    max_population=10000,
    mode_population="object",  # ou "vectorized"

    # Richesse initiale
    initial_total_wealth_V=100000.0,
    gold_factor=1.0,

    # Paramètres RU
    universal_income_rate=0.01,  # DEPRECATED (calculé automatiquement)
    conservation_rate=0.05,      # ρ : taux conservation (0-0.3)

    # Paramètres combustion
    w_S=0.5,  # Poids Stipulat
    w_U=0.5,  # Poids U

    # Modules activés
    enable_demographics=True,
    enable_catastrophes=True,
    enable_price_discovery=True,
    enable_dynamic_business=True,
    enable_business_combustion=True,
    enable_chambre_relance=True,

    # Entreprises
    taux_creation_entreprises=0.05,  # 5% par cycle
    taux_faillite_entreprises=0.03,  # 3% par cycle

    # Reproductibilité
    seed=42
)
```

### 11.2 Exécution et monitoring

```python
# Simulation de 120 cycles (10 ans)
history = {
    "theta": [],
    "kappa": [],
    "eta": [],
    "population": [],
    "V_total": [],
    "U_total": []
}

for t in range(120):
    model.step()

    # Enregistrement historique
    history["theta"].append(model.thermometer())
    history["kappa"].append(model.rad.kappa)
    history["eta"].append(model.rad.eta)
    history["population"].append(len(model.agents))
    history["V_total"].append(sum(a.V_balance for a in model.agents.values()))
    history["U_total"].append(sum(a.U_balance for a in model.agents.values()))

    # Affichage annuel
    if t % 12 == 0:
        year = t // 12
        stats = model.get_statistics()
        print(f"Année {year}:")
        print(f"  θ = {history['theta'][-1]:.4f}")
        print(f"  Population = {history['population'][-1]}")
        print(f"  V total = {history['V_total'][-1]:.2f}")
```

### 11.3 Analyse des résultats

```python
import matplotlib.pyplot as plt
import numpy as np

# Graphique θ
plt.figure(figsize=(12, 8))

plt.subplot(2, 2, 1)
plt.plot(history["theta"])
plt.axhline(y=1.0, color='r', linestyle='--', label='Cible')
plt.title("Évolution du thermomètre θ")
plt.xlabel("Temps (mois)")
plt.ylabel("θ")
plt.legend()

plt.subplot(2, 2, 2)
plt.plot(history["kappa"], label='κ')
plt.plot(history["eta"], label='η')
plt.title("Évolution des coefficients κ et η")
plt.xlabel("Temps (mois)")
plt.legend()

plt.subplot(2, 2, 3)
plt.plot(history["population"])
plt.title("Évolution de la population")
plt.xlabel("Temps (mois)")
plt.ylabel("Nombre d'agents")

plt.subplot(2, 2, 4)
plt.plot(history["V_total"], label='V total')
plt.plot(history["U_total"], label='U total')
plt.title("Évolution des monnaies")
plt.xlabel("Temps (mois)")
plt.legend()

plt.tight_layout()
plt.show()
```

### 11.4 Export des données

```python
import json
import pandas as pd

# Export JSON
with open('simulation_results.json', 'w') as f:
    json.dump(history, f, indent=2)

# Export CSV via pandas
df = pd.DataFrame(history)
df.to_csv('simulation_results.csv', index=False)

# Statistiques finales
final_stats = model.get_statistics()
with open('final_statistics.json', 'w') as f:
    json.dump(final_stats, f, indent=2)
```

### 11.5 Tests de validation

#### Test convergence θ

```python
def test_convergence(model, num_steps=60):
    """Vérifie que θ converge vers 1.0"""
    theta_history = []

    for _ in range(num_steps):
        model.step()
        theta_history.append(model.thermometer())

    # Derniers 20% des cycles
    final_period = theta_history[-int(num_steps*0.2):]
    mean_theta = np.mean(final_period)
    deviation = abs(mean_theta - 1.0)

    assert deviation < 0.3, f"θ ne converge pas : écart = {deviation}"
    print(f"✓ Convergence θ : écart = {deviation:.4f}")
```

#### Test antagonisme

```python
def test_antagonism(model, num_steps=60):
    """Vérifie que κ et η varient différemment"""
    kappa_history = []
    eta_history = []

    for _ in range(num_steps):
        model.step()
        kappa_history.append(model.rad.kappa)
        eta_history.append(model.rad.eta)

    # Calcul variations
    kappa_diff = np.diff(kappa_history)
    eta_diff = np.diff(eta_history)

    # Compter mouvements même sens
    same_direction = np.sum((kappa_diff * eta_diff) > 0)
    ratio = same_direction / len(kappa_diff)

    assert ratio < 0.5, f"Pas d'antagonisme : {ratio*100:.1f}% même sens"
    print(f"✓ Antagonisme actif : {ratio*100:.1f}% mouvements même sens")
```

---

## 12. Dépannage et FAQ

### 12.1 Erreurs courantes

#### ModuleNotFoundError: No module named 'numpy'

**Solution** :
```bash
pip install -r requirements.txt
```

#### AttributeError: 'RADState' object has no attribute 'X'

**Cause** : Champs manquants dans RADState après mise à jour

**Solution** : Vérifier que tous les champs sont définis dans `iris_rad.py` :
- `r_t`, `nu_eff`, `tau_eng` (capteurs)
- `T_period`, `C2_activation_threshold`, `C3_activation_threshold`
- `C3_crisis_counter`, `C3_cooldown_counter`, `C3_max_duration`

#### θ diverge (ne converge pas vers 1.0)

**Causes possibles** :
1. Paramètres tri-capteur mal calibrés
2. Catastrophes trop fréquentes
3. Déséquilibre démographique (naissances >> décès)

**Solution** :
```python
# Vérifier calibration
print(f"α_κ={model.rad.alpha_kappa}, β_κ={model.rad.beta_kappa}, γ_κ={model.rad.gamma_kappa}")
print(f"α_η={model.rad.alpha_eta}, β_η={model.rad.beta_eta}, γ_η={model.rad.gamma_eta}")

# Désactiver temporairement catastrophes
model = IRISEconomy(..., enable_catastrophes=False)
```

### 12.2 Questions fréquentes

#### Pourquoi θ oscille autour de 1.0 au lieu d'être exactement 1.0 ?

**Réponse** : C'est le comportement attendu. Le RAD maintient θ **proche** de 1.0 via rétroaction négative, mais des oscillations amorties sont normales (système dynamique).

#### Quelle est la différence entre V et U ?

**Réponse** :
- **V** : Monnaie de **stock** (épargne, patrimoine)
- **U** : Monnaie de **flux** (revenus courants, éteint annuellement)

#### Pourquoi U est éteint chaque année ?

**Réponse** : U est un **revenu**, pas un actif. L'extinction force la circulation et empêche l'accumulation improductive.

#### Comment choisir conservation_rate (ρ) ?

**Réponse** :
- `ρ = 0.0` : RU maximum (100% de V disponible)
- `ρ = 0.3` : RU minimum (70% de V disponible, 30% conservé)
- **Recommandé** : 0.05 - 0.15 (équilibre entre distribution et conservation)

#### Pourquoi κ et η ont des bornes [0.5, 2.0] ?

**Réponse** : Bornes théoriques pour éviter :
- `< 0.5` : Blocage économique total
- `> 2.0` : Instabilité explosive

#### C'est quoi l'antagonisme algorithmique ?

**Réponse** : Mécanisme qui atténue η quand κ et η varient dans le même sens. Simule l'antagonisme TAP/Staking qui émergera lors de l'implémentation réelle.

#### Pourquoi D a 5 composantes ?

**Réponse** : Reflet sectoriel de la valeur :
- **D_materielle** : Actifs physiques
- **D_services** : Flux d'entretien
- **D_contractuelle** : Engagements productifs
- **D_engagement** : Staking (futur)
- **D_regulatrice** : Chambre de Relance (ajustements)

### 12.3 Optimisation des performances

#### Pour grandes populations (> 1000 agents)

```python
model = IRISEconomy(
    initial_agents=10000,
    mode_population="vectorized",  # Arrays NumPy
    enable_price_discovery=False,   # Désactiver si non nécessaire
    ...
)
```

#### Pour simulations longues (> 500 cycles)

```python
# Enregistrer périodiquement
checkpoint_interval = 100

for t in range(1000):
    model.step()

    if t % checkpoint_interval == 0:
        # Sauvegarder état
        with open(f'checkpoint_{t}.pkl', 'wb') as f:
            pickle.dump(model, f)
```

### 12.4 Ressources supplémentaires

- **Code source** : `/iris/core/`
- **Théorie complète** : `Iris_proto_complet.md`
- **Tests** : `test_antagonism.py`
- **README** : `README.md`

---

## Conclusion

IRIS est un système économique expérimental qui combine :

1. **Théorie thermodynamique** : Conservation, équilibre, régulation
2. **Cybernétique** : Rétroaction négative, capteurs, automatisation
3. **Réalisme économique** : Démographie, entreprises, catastrophes
4. **Innovation monétaire** : Tri-monétaire (V, U, S) + dette thermométrique (D)

Le **RAD** (Régulateur Automatique Décentralisé) est le cœur du système, maintenant automatiquement l'équilibre via un algorithme antagoniste sophistiqué entre κ et η.

Pour toute question ou contribution, n'hésitez pas à consulter le dépôt GitHub ou à contacter l'auteur.

---

**Auteur** : Arnault Nolan
**Date** : 2025
**Version** : 2.0 (avec antagonisme algorithmique)
