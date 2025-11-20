# IRIS - Integrative Resilience Intelligence System

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-2.1.0-green.svg)](https://github.com/Nolan-Ar/Iris_Simulation)

**Système de simulation économique thermodynamique avec régulation automatique décentralisée (RAD)**

---

## 📋 Table des matières

- [Vue d'ensemble](#-vue-densemble)
- [Concepts clés](#-concepts-clés)
- [Installation](#-installation)
- [Démarrage rapide](#-démarrage-rapide)
- [Configuration](#%EF%B8%8F-configuration)
- [Scénarios prédéfinis](#-scénarios-prédéfinis)
- [Utilisation avancée](#-utilisation-avancée)
- [Structure du projet](#-structure-du-projet)
- [Documentation](#-documentation)
- [Développement](#-développement)
- [Licence](#-licence)

---

## 🌟 Vue d'ensemble

IRIS est un système de simulation économique basé sur une approche thermodynamique de l'économie. Il modélise une économie avec :

- **Agents économiques** qui échangent patrimoine (V) et liquidités (U)
- **Entreprises** qui produisent de la valeur via le processus de combustion : S + U → V
- **Régulation automatique décentralisée (RAD)** qui maintient l'équilibre thermodynamique via les coefficients κ (liquidité) et η (efficacité)
- **Démographie**, catastrophes, et dynamiques complexes

### Principes fondamentaux

1. **Thermomètre θ = D / V_on** : indicateur central de la tension économique
2. **Régulation contracyclique** :
   - θ > 1 → κ, η < 1 (freinage)
   - θ < 1 → κ, η > 1 (stimulation)
3. **Convention temporelle** : **1 step = 1 mois** (STEPS_PER_YEAR = 12)
4. **Revenu Universel (RU)** : RU_t = κ_t × V_on × τ / N_agents

---

## 🔑 Concepts clés

### Variables d'état

| Symbole | Nom | Description |
|---------|-----|-------------|
| **V** | Verum (Patrimoine) | Actifs non liquides des agents |
| **U** | Usage (Liquidité) | Monnaie en circulation |
| **D** | Dette thermométrique | Indicateur de tension économique |
| **V_on** | Valeur vivante | Patrimoine actif en circulation |

### Paramètres de régulation (RAD)

| Paramètre | Rôle | Formule |
|-----------|------|---------|
| **κ** (kappa) | Coefficient de liquidité | Régule V→U et le montant de RU |
| **η** (eta) | Efficacité de combustion | Régule le rendement S+U→V |
| **δ_m** | Amortissement mensuel | δ_m ≈ 0.104%/mois ≈ 1.25%/an |
| **θ** | Thermomètre | θ = D / V_on |
| **I** | Indicateur d'inflation | I = ν_eff / ν_target - 1 |

Pour plus de détails, voir [MAPPING_THEORY_CODE.md](MAPPING_THEORY_CODE.md).

---

## 🚀 Installation

### Prérequis

- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)

### Installation rapide

```bash
# Cloner le dépôt
git clone https://github.com/Nolan-Ar/Iris_Simulation.git
cd Iris_Simulation

# Installer les dépendances
make install-dev
# ou
pip install -r requirements.txt
pip install -e .
```

### Installation avec Docker

```bash
# Construire l'image
make docker-build
# ou
docker build -t iris-simulation .

# Lancer une simulation
make docker-run
```

---

## ⚡ Démarrage rapide

### Simulation de base

```bash
# Simulation par défaut (100 steps = ~8 ans)
python -m iris.simulations.run_simulation

# Simulation de 50 ans avec 1000 agents
python -m iris.simulations.run_simulation --years 50 --population 1000
```

### Utilisation du Makefile

```bash
# Afficher l'aide
make help

# Simulation baseline stable (100 ans)
make sim-baseline

# Test de crise avec volatilité élevée
make sim-crisis

# Système sans régulation (témoin)
make sim-no-regulation
```

### Utilisation avec scénarios

```bash
# Charger un scénario prédéfini
python -m iris.simulations.run_simulation --scenario baseline_stable

# Charger une configuration personnalisée
python -m iris.simulations.run_simulation --config my_config.yaml

# Override avec CLI
python -m iris.simulations.run_simulation --scenario crisis --steps 100 --population 500
```

---

## ⚙️ Configuration

### Fichier config.yaml

Le fichier `config.yaml` centralise tous les paramètres :

```yaml
simulation:
  rad:
    kappa_beta: 0.5      # Sensibilité de κ
    eta_alpha: 0.5       # Sensibilité de η
    kappa_smoothing: 0.1 # Lissage de κ
    eta_smoothing: 0.15  # Lissage de η
    delta_m: 0.001041666 # Amortissement mensuel

modules:
  enable_demographics: true
  enable_catastrophes: false
  enable_businesses: true
  enable_business_combustion: true

temporal:
  steps_per_year: 12  # 1 step = 1 mois
```

### Priorité de configuration

```
CLI args > Scenario config > config.yaml > Defaults
```

**Exemple** :
```bash
# Ce qui suit charge baseline_stable mais override la durée
python -m iris.simulations.run_simulation --scenario baseline_stable --steps 600
```

---

## 🎯 Scénarios prédéfinis

### 1. baseline_stable
**Objectif** : Démontrer l'équilibre stable sur 100 ans

```bash
make sim-baseline
# ou
python -m iris.simulations.run_simulation --scenario baseline_stable
```

- **Durée** : 1200 steps (100 ans)
- **Population** : 1000 agents
- **Modules** : Démographie ✓, Entreprises ✓, Catastrophes ✗
- **Usage** : Validation de l'équilibre θ ≈ 1 à long terme

### 2. crisis_high_volatility
**Objectif** : Stress test avec catastrophes fréquentes

```bash
make sim-crisis
```

- **Durée** : 600 steps (50 ans)
- **Catastrophes** : 20% (vs 5% normal)
- **RAD** : Régulation hyper-réactive (κ_beta=0.8, η_alpha=0.8)
- **Usage** : Test de résilience du système

### 3. no_regulation
**Objectif** : Système témoin sans régulation RAD

```bash
make sim-no-regulation
```

- **Durée** : 1000 steps (~83 ans)
- **Régulation** : κ=η=1 fixe (désactivée)
- **Usage** : Comparaison avec système régulé

### 4. regulation_only
**Objectif** : Illustration pure de la régulation RAD

```bash
make sim-regulation-only
```

- **Durée** : 500 steps (~42 ans)
- **Modules complexes** : Tous désactivés
- **Usage** : Thèse, démonstration théorique

### 5. large_scale
**Objectif** : Grande échelle avec optimisations

- **Population** : 100,000 agents
- **Optimisations** : Vectorisation, multiprocessing
- **Usage** : Simulations à grande échelle

---

## 🔬 Utilisation avancée

### Visualisations pour la thèse

```python
from iris.core.iris_scenarios import ScenarioRunner
from iris.analysis.iris_visualizer import IRISVisualizer

# Lancer le scénario baseline
runner = ScenarioRunner(n_agents=1000)
economy = runner.run_baseline_stable(steps=1200)

# Générer le pack de visualisations complet
viz = IRISVisualizer()
viz.plot_thesis_pack(economy.history, scenario_name="baseline_stable")
```

**Figures générées** :
1. Paramètres de régulation (r, η, κ)
2. Revenu Universel par tête
3. Valeur vivante en circulation (V_on)
4. Distribution de richesse et Gini

Voir [figures_doc.md](figures_doc.md) pour les légendes détaillées.

### Validation Monte Carlo

```bash
# Lancer 100 simulations avec analyse statistique
make validate

# ou directement
python -m iris.core.iris_validation --monte-carlo --runs 100
```

### Tests

```bash
# Tous les tests
make test

# Tests unitaires uniquement
make test-unit

# Avec couverture
make test-coverage
```

### Code quality

```bash
# Linting
make lint

# Formatage automatique (black + isort)
make format

# Type checking
make typecheck

# Tout vérifier
make check-all
```

---

## 📁 Structure du projet

```
Iris_Simulation/
├── iris/
│   ├── core/                    # Cœur du modèle
│   │   ├── iris_model.py        # Modèle économique principal
│   │   ├── iris_rad.py          # Régulation RAD (κ, η, δ)
│   │   ├── iris_scenarios.py    # Scénarios prédéfinis
│   │   ├── iris_entreprises.py  # Gestion des entreprises
│   │   ├── iris_demographics.py # Naissances/décès
│   │   ├── iris_catastrophes.py # Événements catastrophiques
│   │   └── ...
│   ├── analysis/                # Analyse et visualisation
│   │   ├── iris_visualizer.py   # Graphiques et pack thèse
│   │   └── iris_validation.py   # Validation Monte Carlo
│   ├── simulations/             # Scripts de simulation
│   │   ├── run_simulation.py    # Point d'entrée principal
│   │   └── performance_test.py  # Tests de performance
│   ├── utils/                   # Utilitaires
│   │   ├── config_loader.py     # Chargement config.yaml
│   │   ├── validation.py        # Validations numériques
│   │   └── ...
│   └── tests/                   # Tests unitaires
├── config.yaml                  # Configuration centrale
├── MAPPING_THEORY_CODE.md       # Mapping théorie ↔ code
├── figures_doc.md               # Documentation des figures
├── Dockerfile                   # Conteneur Docker
├── Makefile                     # Automatisation
├── requirements.txt             # Dépendances Python
├── setup.py                     # Installation du package
└── README.md                    # Ce fichier
```

---

## 📚 Documentation

### Documents de référence

- **[MAPPING_THEORY_CODE.md](MAPPING_THEORY_CODE.md)** : Mapping complet entre symboles théoriques et code
  - Table des 50+ paramètres avec rôle économique
  - Formules mathématiques et localisation dans le code
  - Explication du rôle central de κ

- **[figures_doc.md](figures_doc.md)** : Documentation des visualisations
  - Légendes détaillées pour chaque figure du pack thèse
  - Formules et interprétations
  - Exemples d'utilisation

### Docstrings

Le code est abondamment documenté :
```python
# Exemple: iris/core/iris_model.py
def distribute_universal_income(self):
    """
    Distribution du Revenu Universel (RU)

    ÉCHELLE TEMPORELLE : 1 step = 1 mois
    Distribué tous les 12 steps (annuellement)

    Formule : RU_t = κ_t × (V_on × τ) / N_agents

    κ MODULE ICI LA LIQUIDITÉ (MONTANT DE RU DISTRIBUÉ)
    """
```

---

## 🛠️ Développement

### Contribuer

1. Fork le projet
2. Créer une branche (`git checkout -b feature/ma-feature`)
3. Commit les changements (`git commit -m 'Add ma-feature'`)
4. Push vers la branche (`git push origin feature/ma-feature`)
5. Ouvrir une Pull Request

### Guidelines

- **Code style** : Black (line-length=100), isort
- **Type hints** : Utiliser mypy
- **Tests** : pytest avec >80% coverage
- **Documentation** : Docstrings pour toutes les fonctions publiques
- **Convention temporelle** : Toujours préciser "1 step = 1 mois"

### Environnement de développement

```bash
# Installation complète avec dépendances dev
make install-dev

# Formater le code
make format

# Vérifier avant commit
make check-all
```

### Tests de performance

```bash
# Test de performance
python -m iris.simulations.performance_test

# ou via Makefile
make run-performance
```

---

## 🐳 Docker

### Construction

```bash
make docker-build
```

### Exécution

```bash
# Simulation par défaut avec volumes persistants
make docker-run

# Shell interactif
make docker-shell

# Scénario spécifique
docker run --rm \
  -v $(pwd)/simulation_results:/app/simulation_results \
  iris-simulation \
  python -m iris.simulations.run_simulation --scenario baseline_stable
```

---

## 📊 Résultats et exports

Les simulations génèrent automatiquement :

```
data/
  └── history.csv          # Historique complet de la simulation

plots/
  ├── regulation_params.png    # Évolution r, η, κ
  ├── universal_income.png     # RU par tête
  ├── circulating_value.png    # V_on
  └── wealth_distribution.png  # Gini + distribution

simulation_results/
  └── [timestamps]/        # Résultats horodatés
```

---

## 🔍 FAQ

### Quelle est la convention temporelle ?

**1 step = 1 mois** (STEPS_PER_YEAR = 12). Tous les taux et fréquences sont exprimés en conséquence.

### Quelle est la différence entre V et U ?

- **V (Verum)** : Patrimoine/actifs non liquides (immobilier, entreprises, etc.)
- **U (Usage)** : Liquidités/monnaie en circulation pour les transactions

### Comment fonctionne la régulation RAD ?

Le RAD ajuste automatiquement :
1. **κ (kappa)** : Régule la liquidité (conversion V→U et montant de RU)
2. **η (eta)** : Régule l'efficacité de production (S+U→V)

En mode contracyclique :
- **Surchauffe** (θ > 1) : κ ↓, η ↓ → freine l'économie
- **Sous-activité** (θ < 1) : κ ↑, η ↑ → stimule l'économie

### Puis-je désactiver certains modules ?

Oui, via `config.yaml` ou CLI :

```bash
# Sans démographie ni catastrophes
python -m iris.simulations.run_simulation \
  --no-demographics \
  --no-catastrophes
```

### Comment reproduire une simulation ?

Utiliser `--seed` :

```bash
python -m iris.simulations.run_simulation --seed 42
```

---

## 📄 Licence

MIT License - voir [LICENSE](LICENSE) pour plus de détails.

---

## 👤 Auteur

**Arnault Nolan**
📧 Email: arnaultnolan@gmail.com
🔗 GitHub: [Nolan-Ar](https://github.com/Nolan-Ar)

---

## 🙏 Remerciements

Ce projet s'inscrit dans une thèse de recherche sur les systèmes économiques thermodynamiques et la régulation automatique décentralisée.

---

## 📈 Roadmap

- [ ] Interface web interactive
- [ ] Export vers formats économétriques standards
- [ ] Intégration de données réelles
- [ ] Module d'apprentissage par renforcement pour optimiser RAD
- [ ] API REST pour simulations à la demande

---

**Version** : 2.1.0
**Dernière mise à jour** : Novembre 2025
