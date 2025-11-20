# IRIS Economic System

**Système Économique IRIS** (Integrative Resilience Intelligence System)

Un modèle de simulation économique basé sur la preuve d'acte plutôt que la promesse de remboursement, avec régulation automatique multi-couches.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Status](https://img.shields.io/badge/Status-Active-success)](https://github.com/Nolan-Ar/Iris_Simulation)
[![Version](https://img.shields.io/badge/Version-2.1.0-orange)](https://github.com/Nolan-Ar/Iris_Simulation)

---

## 📋 Table des matières

- [Vue d'ensemble](#-vue-densemble)
- [Architecture du projet](#-architecture-du-projet)
- [Installation](#-installation)
- [Démarrage rapide](#-démarrage-rapide)
- [Simulations disponibles](#-simulations-disponibles)
- [Résultats et performances](#-résultats-et-performances)
- [Documentation](#-documentation)
- [Tests et validation](#-tests-et-validation)
- [Contribution](#-contribution)

---

## 🎯 Vue d'ensemble

IRIS est un système économique innovant qui utilise trois monnaies complémentaires :

- **V (Verum)** : Mémoire de valeur / patrimoine ancré
- **U (Usage)** : Monnaie d'usage quotidien (non-accumulable)
- **D (Dette)** : Miroir thermométrique pour la régulation (PAS juridiquement exigible)

### Caractéristiques principales

✅ **Régulation automatique** : RAD (Réserve d'Actifs Détruits) avec architecture multi-couches C1/C2/C3
✅ **Démographie dynamique** : Naissances, décès, vieillissement, transmission patrimoniale
✅ **Catastrophes aléatoires** : Chocs naturels, économiques, politiques, technologiques
✅ **Entreprises évolutives** : Créations, croissance, faillites avec combustion S+U→V
✅ **Découverte de prix** : Marchés sectoriels avec offre/demande explicite
✅ **Validation académique** : Monte Carlo, tests statistiques, analyses de sensibilité
✅ **Performance optimisée** : Backend vectorisé NumPy pour simulations massives (50k+ agents)
✅ **Double architecture** : Mode "object" (détaillé, NFT) et mode "vectorized" (rapide, grandes échelles)

### Statistiques du projet

- **9,121 lignes de code** Python sur 19 fichiers
- **Cœur du système** : `iris_model.py` (2,175 lignes)
- **Module de validation** : `iris_validation.py` (1,201 lignes)
- **Backend vectorisé** : `iris_population_vectorized.py` (208 lignes)
- **Tests de performance** : Scalabilité quasi-linéaire jusqu'à 100k+ agents en mode vectorisé

---

## 📁 Architecture du projet

```
Iris_Simulation/
├── README.md                                    # Ce fichier
├── requirements.txt                             # Dépendances Python
├── integrative resilience intelligence system.docx  # Spécifications théoriques
│
├── iris/                                        # Code source principal
│   ├── __init__.py
│   │
│   ├── core/                                    # Moteur économique (7,558 lignes)
│   │   ├── __init__.py
│   │   ├── iris_model.py                        # CŒUR: Modèle économique complet (2,166 lignes)
│   │   ├── iris_validation.py                   # Tests académiques (1,201 lignes)
│   │   ├── iris_demographics.py                 # Démographie dynamique (677 lignes)
│   │   ├── iris_visualizer.py                   # Graphiques et dashboards (579 lignes)
│   │   ├── iris_comptes_entreprises.py          # Comptabilité entreprises (546 lignes)
│   │   ├── iris_scenarios.py                    # Scénarios de test (512 lignes)
│   │   ├── iris_entreprises.py                  # Gestion entreprises (455 lignes)
│   │   ├── iris_catastrophes.py                 # Chocs aléatoires (448 lignes)
│   │   ├── iris_chambre_relance.py              # Redistribution actifs (438 lignes)
│   │   ├── iris_prix.py                         # Découverte de prix (398 lignes)
│   │   ├── iris_oracle.py                       # Ancrage cadastral (395 lignes)
│   │   └── iris_population_vectorized.py        # Backend vectorisé NumPy (208 lignes)
│   │
│   ├── simulations/                             # Scripts d'exécution
│   │   ├── __init__.py
│   │   ├── run_simulation.py                    # Script universel v2.1 (306 lignes)
│   │   └── performance_test.py                  # Tests de performance (279 lignes)
│   │
│   ├── analysis/                                # Analyse et visualisation
│   │   ├── __init__.py
│   │   └── iris_visualizer.py                   # Visualisations (579 lignes)
│   │
│   └── tests/                                   # Tests unitaires
│       └── test_comptes_entreprises.py          # Tests comptes (358 lignes)
│
├── simulation/                                  # Documentation technique
│   └── DOCUMENTATION.md                         # Documentation complète (41.9 KB)
│
├── performance_data/                            # Résultats de performance
│   ├── ANALYSE_RESULTATS.md                     # Analyse des résultats
│   ├── history_*_*.csv                          # Historiques de simulation
│   ├── performance_summary_*.json               # Résumés performance
│   └── step_times_*_*.csv                       # Temps d'exécution
│
└── validation_results/                          # Résultats de validation
    ├── VALIDATION_IRIS.md                       # Rapport de validation
    ├── monte_carlo_results.json                 # Résultats Monte Carlo
    └── sensitivity_eta_alpha.json               # Analyse de sensibilité
```

---

## 🛠️ Installation

### Prérequis

- Python 3.8+
- pip

### Dépendances

```bash
pip install -r requirements.txt
```

Dépendances principales :
- `numpy >= 1.21.0` - Calculs numériques, vectorisation
- `pandas >= 1.3.0` - Gestion données CSV, historique
- `matplotlib >= 3.4.0` - Visualisations graphiques
- `seaborn >= 0.11.0` - Thèmes et styles graphiques

### Clonage du projet

```bash
git clone https://github.com/Nolan-Ar/Iris_Simulation.git
cd Iris_Simulation
```

---

## 🚀 Démarrage rapide

### Simulation de base (100 agents, 100 ans)

```bash
cd iris/simulations
python run_simulation.py --population 100 --years 100
```

### Simulation avec visualisations

```bash
python run_simulation.py --population 100 --years 100 --visualize
```

### Simulation longue durée (1000 agents, 500 ans)

```bash
python run_simulation.py --population 1000 --years 500 --max-population 10000 --visualize
```

### Test de performance

```bash
python performance_test.py
```

---

## 📊 Simulations disponibles

### Script universel : `run_simulation.py`

Ce script unifié (v2.1) remplace tous les anciens scripts et offre toutes les fonctionnalités.

#### Options principales

```bash
python run_simulation.py [OPTIONS]

Options:
  --population N              # Nombre d'agents initiaux (défaut: 100)
  --years YEARS               # Durée en années (défaut: 100)
  --max-population N          # Population maximale (défaut: 10000)
  --initial-total-V VALUE     # Richesse initiale totale (défaut: auto ~5.78 V/agent)

  # Modules optionnels
  --no-demographics           # Désactive démographie dynamique
  --no-catastrophes           # Désactive catastrophes aléatoires
  --no-prices                 # Désactive découverte de prix
  --no-business               # Désactive entreprises dynamiques

  # Backend de population
  --mode-population MODE      # "object" (détaillé, NFT) ou "vectorized" (rapide, grandes populations)

  # Reproductibilité et sortie
  --seed SEED                 # Graine aléatoire pour reproductibilité
  --visualize                 # Génère graphiques automatiquement
  --output-dir DIR            # Répertoire de sortie (défaut: résultats/)
```

#### Exemples d'utilisation

**Simulation standard (démographie + catastrophes + entreprises + prix)** :
```bash
python run_simulation.py --population 200 --years 100 --visualize
```

**Simulation académique (reproductible)** :
```bash
python run_simulation.py --population 100 --years 500 --seed 42 --output-dir analyses_iris/sim_500ans
```

**Simulation sans catastrophes (étude de stabilité)** :
```bash
python run_simulation.py --population 150 --years 200 --no-catastrophes --visualize
```

**Simulation grande population (backend vectorisé)** :
```bash
python run_simulation.py --population 50000 --years 200 --mode-population vectorized --max-population 100000
```

**Simulation avec backend détaillé (mode objet, NFT)** :
```bash
python run_simulation.py --population 100 --years 100 --mode-population object --visualize
```

### Test de performance : `performance_test.py`

Lance des tests de scalabilité avec 100, 500 et 1000 agents.

```bash
python performance_test.py
```

**Résultats typiques (mode objet)** :
| Population | Temps/step | Scalabilité |
|-----------|-----------|-------------|
| 100       | 3.81 ms   | Baseline    |
| 500       | 16.06 ms  | 4.2x        |
| 1000      | 38.37 ms  | 10.1x       |

**Résultats typiques (mode vectorisé)** :
| Population | Temps/step | Gain vs objet |
|-----------|-----------|---------------|
| 1k        | ~5 ms     | ×8            |
| 10k       | ~15 ms    | ×25           |
| 50k       | ~75 ms    | ×100+         |
| 100k      | ~150 ms   | ×250+         |

**Observation** : Mode object = scalabilité quasi-linéaire excellent jusqu'à 1000 agents.
Mode vectorized = performances ×10-×500 pour grandes populations (zéro boucle Python, tout en NumPy SIMD).

---

## 📈 Résultats et performances

### Résultats de validation (Monte Carlo)

Fichier : `validation_results/monte_carlo_results.json`

**Configuration** : 5 runs × 20 cycles

**Résultats** :
- **θ moyen** : 0.9837 (très proche de 1.0)
- **Écart-type** : 0.0016 (robuste)
- **IC 95%** : [0.9817, 0.9857]
- **Taux convergence** : 100%
- **Taux crash** : 0%
- **Oscillations** : 0.0047 (faibles)

**Conclusion** : ✅ Stabilité numérique confirmée

### Résultats de performance (100-1000 agents, 100 ans)

Fichier : `performance_data/ANALYSE_RESULTATS.md`

**Tests** : 19 novembre 2025

| Population | Thermomètre θ | Gini | Croissance pop |
|-----------|---------------|------|----------------|
| 100       | 0.6297        | 0.5959 | ×3.32        |
| 500       | 0.6116        | 0.5578 | ×2.88        |
| 1000      | 0.6217        | 0.5425 | ×3.13        |

**Observations** :
- Régulation RAD efficace (θ ≈ 0.6)
- Inégalités modérées (Gini ≈ 0.55)
- Forte croissance démographique (×3)
- 9 catastrophes observées sur 100 ans

### Analyse de sensibilité

Fichier : `validation_results/sensitivity_eta_alpha.json`

**Paramètre testé** : `eta_alpha` (±10%)

**Résultats** :
- **Élasticité θ** : -0.015 (peu sensible)
- **Élasticité Gini** : 0.269 (sensibilité modérée)

**Conclusion** : Système robuste aux variations de paramètres.

### Fichiers de sortie

Les résultats sont sauvegardés dans le répertoire spécifié :

- **`history.csv`** : Historique complet avec toutes les métriques
  - time, total_V, total_U, total_D
  - thermometer, indicator, kappa, eta
  - gini_coefficient, population, avg_age
  - births, deaths, catastrophes
  - C2_activated, C3_activated

- **`summary.txt`** : Résumé statistique de la simulation

- **Graphiques PNG** (si `--visualize`) :
  - Évolution V, U, D
  - Thermomètre θ et indicateur I
  - Coefficient de Gini
  - Coefficients κ et η
  - Population et âge moyen
  - Activations RAD (C2, C3)

---

## 📚 Documentation

### Documentation complète

**Fichier principal** : `simulation/DOCUMENTATION.md` (41.9 KB)

Sections couvertes :
1. Vue d'ensemble du système IRIS
2. Architecture complète
3. Concepts fondamentaux (V, U, D, θ, I, κ, η)
4. Modules principaux (détails de chaque module)
5. Features et fonctionnalités
6. Guide d'utilisation
7. Exemples d'exécution
8. Analyse des résultats
9. Références théoriques

### Spécifications théoriques

**Fichier** : `integrative resilience intelligence system.docx` (122 KB)

Document Word contenant les spécifications théoriques complètes du système IRIS.

### Concepts théoriques clés

#### RAD (Réserve d'Actifs Détruits)

Architecture multi-couches :
- **C1** : Régulation légère continue (ajuste κ et η chaque cycle)
- **C2** : Régulation profonde (tous les 12 cycles si |I| > 15%)
- **C3** : Rebalancement d'urgence (si |I| > 30%)

#### Oracle d'émission cadastrale

Garantit l'équilibre initial V₀ = D₀ et la traçabilité complète via NFT.

**Formule d'ancrage** :
```
V₀ = Valeur_estimée × Φ_or × (1 - r_zone/100) × Φ_auth
```

#### Chambre de Relance

Récupère actifs orphelins et redistribue selon schéma 60/30/10 :
- 60% → Revenu Universel
- 30% → Investissements
- 10% → Gouvernance

**Impact déflationniste** : ΔD = -0.3 × Pool_CR

#### Comptes Entreprises

**Mécanisme de combustion** : S + U → V

**Distribution organique 40/60** :
- 40% → Masse salariale (en U)
- 60% → Trésorerie (en V)

**NFT Financiers** : Titres productifs avec rendement (2.5% à 5% selon type).

---

## 🧪 Tests et validation

### Tests unitaires

```bash
cd iris/tests
python -m pytest test_comptes_entreprises.py
```

**Tests implémentés** :
1. Distribution 40/60 combustion
2. Limites rétention V_operationnel
3. Conversion NFT financiers
4. Registre centralisé collecte masses salariales
5. Intégration IRISEconomy

### Validation Monte Carlo

```python
from iris.core.iris_validation import IRISValidator

validator = IRISValidator()

# Lance 100 simulations de 100 cycles
mc_results = validator.run_monte_carlo(n_runs=100, steps=100)

print(f"θ moyen: {mc_results.theta_mean:.4f}")
print(f"IC 95%: [{mc_results.theta_ci_lower:.4f}, {mc_results.theta_ci_upper:.4f}]")
print(f"Taux convergence: {mc_results.convergence_rate*100:.1f}%")
```

### Validation rapide (Quick Validation)

```python
from iris.core.iris_validation import quick_validation

# Lance 50 runs + tests statistiques
mc_results, ks_results = quick_validation(n_runs=50, steps=100)
# Résultats sauvegardés dans validation_results/
```

### Analyse de sensibilité

```python
# Test sensibilité d'un paramètre RAD
sens_results = validator.run_sensitivity_analysis(
    parameter_name='eta_alpha',
    baseline_value=0.5,
    variation_pct=[-10, -5, 0, 5, 10],
    n_runs_per_variation=20,
    steps=100
)

print(f"Élasticité θ: {sens_results.theta_elasticity:.4f}")
```

### Scénarios de résilience

```python
from iris.core.iris_scenarios import ScenarioRunner

runner = ScenarioRunner(n_agents=100, output_dir="results")

# Test différents chocs
economy_base = runner.run_baseline(steps=1000)
economy_shock = runner.run_wealth_loss_shock(steps=1000, magnitude=0.3)
economy_crisis = runner.run_systemic_crisis(steps=1500)

# Comparaison
runner.compare_scenarios(shock_time=500)
```

---

## 🤝 Contribution

### Workflow de développement

1. Fork du projet
2. Créer une branche (`git checkout -b feature/amazing-feature`)
3. Commit des changements (`git commit -m 'Add amazing feature'`)
4. Push vers la branche (`git push origin feature/amazing-feature`)
5. Ouvrir une Pull Request

### Guidelines

- Code Python conforme PEP 8
- Documentation docstrings pour toutes les fonctions
- Tests unitaires pour nouvelles fonctionnalités
- Mise à jour de la documentation (README.md et DOCUMENTATION.md)
- Validation Monte Carlo pour modifications du cœur RAD

---

## 📝 Licence

Ce projet est sous licence MIT.

---

## 👤 Auteur

**Arnault Nolan**
- Email: arnaultnolan@gmail.com
- GitHub: [@Nolan-Ar](https://github.com/Nolan-Ar)

---

## 🙏 Remerciements

Basé sur les travaux théoriques en :

### Cybernétique
- Wiener : *Cybernetics* (1948)
- Ashby : *Introduction to Cybernetics* (1956)
- Beer : *Brain of the Firm* (1972)

### Thermodynamique économique
- Georgescu-Roegen : *The Entropy Law and the Economic Process* (1971)
- Ayres : *Energy, Complexity and Wealth Maximization* (2016)

### Anthropologie économique
- Graeber : *Debt: The First 5000 Years* (2011)
- Polanyi : *The Great Transformation* (1944)
- Mauss : *The Gift* (1925)

### Validation et Vérification
- Sargent, R.G. (2013) : "Verification and validation of simulation models", *Journal of Simulation*
- Kleijnen, J.P.C. (1995) : "Verification and validation of simulation models", *European Journal of Operational Research*

---

## 📊 Métriques du projet

**Dernière mise à jour** : 19 novembre 2025
**Version** : 2.1.0
**Statut** : Production
**Lignes de code** : 9,121 lignes Python
**Modules** : 19 fichiers
**Tests** : Validation Monte Carlo + Tests unitaires
**Performance** : Scalabilité quasi-linéaire jusqu'à 1000+ agents

---

## 🔗 Liens utiles

- **Documentation technique** : `simulation/DOCUMENTATION.md`
- **Spécifications théoriques** : `integrative resilience intelligence system.docx`
- **Résultats de validation** : `validation_results/`
- **Résultats de performance** : `performance_data/`

---

**IRIS** - *Un système économique résilient basé sur la preuve d'acte*
