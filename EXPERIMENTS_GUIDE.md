# Guide des Expériences IRIS

## 🎯 Vue d'ensemble

Le système d'expériences IRIS permet de tester systématiquement l'effet de différents paramètres sur la stabilité économique du système.

## 📦 Modules créés

### 1. `iris/simulations/experiment_grid.py`

**Grille d'expériences paramétriques complète**

- **Grille de paramètres** :
  - `initial_agents` : 200, 500, 1000
  - `enable_catastrophes` : True, False
  - `conservation_rate` : 0.0, 0.05, 0.15
  - `seed` : 1, 2, 3
  - `steps` : 600, 1200 (50 ou 100 ans)

- **Total combinaisons** : 3 × 2 × 3 × 3 × 2 = **108 expériences**

### 2. `iris/simulations/generate_report.py`

**Générateur de rapports d'analyse automatiques**

- Analyse statistique complète
- Comparaisons paramétriques
- Identification configuration optimale
- Recommandations

### 3. `iris/analysis/iris_visualizer.py`

**Visualisation des résultats**

- Graphiques matplotlib (θ, κ/η, population, Gini)
- Export JSON des données
- Sauvegarde automatique PNG

## 🚀 Utilisation

### Test rapide (4 expériences, ~10 minutes)

```bash
python test_experiment_small.py
```

**Scénarios testés** :
1. Baseline : N=100, catastrophes OFF, ρ=0.05
2. Avec catastrophes : N=100, catastrophes ON, ρ=0.05
3. Sans conservation : N=100, catastrophes OFF, ρ=0.0
4. Grande population : N=200, catastrophes OFF, ρ=0.05

**Résultats** :
- `results/test_grid/` : répertoires par scénario
- `results/test_grid/summary.csv` : résumé global
- `results/test_grid/RAPPORT_ANALYSE.md` : rapport automatique

### Grille complète (108 expériences, ~2-3 heures)

```bash
python -m iris.simulations.experiment_grid
```

**⚠️ Attention** : Cette commande lance 108 simulations complètes !

**Résultats** :
- `results/grid/<scenario_name>/` : répertoire par scénario
  - `history.csv` : historique complet (toutes les variables)
  - `main_variables.png` : graphiques
  - `data_<scenario>.json` : données brutes
- `results/grid/summary.csv` : résumé global (1 ligne par scénario)

### Génération de rapport d'analyse

```bash
python -m iris.simulations.generate_report results/test_grid
```

**Génère** : `results/test_grid/RAPPORT_ANALYSE.md`

**Contenu** :
- Statistiques globales (θ, Gini, population)
- Analyse convergence et stabilité
- Effet des paramètres
- Scénarios optimaux
- Recommandations

## 📊 Structure des résultats

### Fichier `summary.csv` (24 colonnes)

| Colonne | Description |
|---------|-------------|
| `scenario_name` | Nom du scénario (ex: N200_cata1_rho005_seed1_t600) |
| `initial_agents` | Population initiale |
| `enable_catastrophes` | Catastrophes activées (True/False) |
| `conservation_rate` | Taux conservation ρ (0.0-0.3) |
| `seed` | Graine aléatoire |
| `steps` | Nombre de cycles simulés |
| `theta_mean` | Moyenne du thermomètre θ |
| `theta_std` | Écart-type de θ (stabilité) |
| `theta_final` | θ final |
| `theta_min` | θ minimum |
| `theta_max` | θ maximum |
| `gini_mean` | Gini moyen (inégalités) |
| `gini_std` | Écart-type Gini |
| `gini_final` | Gini final |
| `catastrophes_total` | Nombre total de catastrophes |
| `catastrophes_mean` | Catastrophes moyennes par cycle |
| `population_initial` | Population initiale |
| `population_final` | Population finale |
| `population_mean` | Population moyenne |
| `kappa_mean` | κ moyen |
| `eta_mean` | η moyen |
| `C2_activations` | Activations C2 (régulation profonde) |
| `C3_activations` | Activations C3 (urgence) |
| `elapsed_time_s` | Temps d'exécution (secondes) |

### Fichier `history.csv` (par scénario)

Historique complet cycle par cycle :
- `time` : temps (mois)
- `thermometer` : θ
- `indicator` : I = θ - 1
- `kappa`, `eta` : coefficients de régulation
- `population` : nombre d'agents
- `total_V`, `total_U`, `total_D`, `V_on` : agrégats monétaires
- `gini_coefficient` : inégalité de richesse
- `catastrophes`, `births`, `deaths` : événements
- `C2_activated`, `C3_activated` : régulation activée

## 🔍 Résultats du test rapide

**Configuration testée** : 4 scénarios, 120 cycles (10 ans)

### Résultats clés

✅ **Convergence θ** :
- θ moyen = 1.0011 (excellente convergence)
- Écart à cible = 0.0011

✅ **Stabilité** :
- θ std = 0.0152 (excellente stabilité)
- Oscillations très amorties

✓ **Inégalités** :
- Gini moyen = 0.56 (inégalité modérée)

✅ **Régulation** :
- 0 activations C2
- 0 activations C3 (système stable)

⚡ **Performance** :
- ~0.15s par simulation (120 cycles)
- Total : 0.6s pour 4 scénarios

### Configuration optimale identifiée

```python
ExperimentConfig(
    initial_agents=200,
    enable_catastrophes=False,
    conservation_rate=0.05,
    seed=1,
    steps=120
)
```

**Résultats** :
- θ = 1.0615 ± 0.0099 (très stable)
- Gini = 0.574
- Population finale = 235

### Observations principales

1. **Effet catastrophes** :
   - Catastrophes ON → θ_std +19% (moins stable)
   - Catastrophes ON → Population -22%

2. **Effet conservation ρ** :
   - ρ = 0.0 (RU max) → Gini 0.552
   - ρ = 0.05 (RU standard) → Gini 0.562

3. **Effet population** :
   - N = 100 → θ_std = 0.0169
   - N = 200 → θ_std = 0.0099 (plus stable)

## 📈 Analyse avancée

### Charger les résultats en Python

```python
import pandas as pd
import matplotlib.pyplot as plt

# Charger le résumé
df = pd.read_csv('results/test_grid/summary.csv')

# Filtrer par paramètre
catastrophes_on = df[df['enable_catastrophes'] == True]
catastrophes_off = df[df['enable_catastrophes'] == False]

# Comparaison
print(f"θ_std (catastrophes ON):  {catastrophes_on['theta_std'].mean():.4f}")
print(f"θ_std (catastrophes OFF): {catastrophes_off['theta_std'].mean():.4f}")

# Graphique
plt.figure(figsize=(10, 6))
plt.scatter(df['theta_mean'], df['gini_final'],
            c=df['enable_catastrophes'], cmap='coolwarm')
plt.xlabel('θ moyen')
plt.ylabel('Gini final')
plt.colorbar(label='Catastrophes')
plt.title('Convergence θ vs Inégalités (Gini)')
plt.show()
```

### Charger un historique spécifique

```python
# Charger historique d'un scénario
scenario = 'N100_cata1_rho005_seed1_t120'
history = pd.read_csv(f'results/test_grid/{scenario}/history.csv')

# Graphique θ
plt.figure(figsize=(12, 4))
plt.plot(history['time'], history['thermometer'], label='θ')
plt.axhline(y=1.0, color='r', linestyle='--', label='Cible')
plt.xlabel('Temps (mois)')
plt.ylabel('θ')
plt.title(f'Évolution θ - {scenario}')
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()
```

## 🎨 Graphiques générés

Pour chaque scénario, le visualiseur génère automatiquement :

### `main_variables.png`

Grille 2×2 avec :
1. **Thermomètre θ** : convergence vers 1.0
2. **Coefficients κ et η** : régulation antagoniste
3. **Population** : dynamique démographique
4. **Gini** : évolution des inégalités

## 🔧 Personnalisation

### Modifier la grille de paramètres

Éditer `iris/simulations/experiment_grid.py` :

```python
param_grid = {
    'initial_agents': [100, 500, 1000, 2000],  # Ajouter 2000
    'enable_catastrophes': [True, False],
    'conservation_rate': [0.0, 0.05, 0.10, 0.15],  # Ajouter 0.10
    'seed': [1, 2, 3, 4, 5],  # Ajouter graines 4 et 5
    'steps': [600, 1200, 2400]  # Ajouter simulations longues
}
```

### Créer une grille personnalisée

```python
from iris.simulations.experiment_grid import ExperimentConfig, run_single_experiment
from pathlib import Path

# Définir vos scénarios
custom_configs = [
    ExperimentConfig(initial_agents=150, enable_catastrophes=True,
                     conservation_rate=0.08, seed=42, steps=240),
    ExperimentConfig(initial_agents=300, enable_catastrophes=False,
                     conservation_rate=0.12, seed=42, steps=360),
]

# Lancer
output_dir = Path("results/custom")
for config in custom_configs:
    run_single_experiment(config, output_dir)
```

## 📝 Rapport d'analyse type

Le rapport généré contient :

### 1. Résumé Global
- Statistiques générales (moyenne, écart-type, min, max)
- Métriques : θ, Gini, population, catastrophes

### 2. Convergence θ
- Scénarios les plus stables (θ_std faible)
- Scénarios les moins stables (θ_std élevé)

### 3. Effet des Paramètres
- Impact catastrophes (ON vs OFF)
- Impact ρ (conservation rate)
- Impact population initiale

### 4. Inégalités (Gini)
- Scénarios les plus égalitaires
- Scénarios les plus inégalitaires

### 5. Régulation C2/C3
- Activations C2 (régulation profonde)
- Activations C3 (urgence)
- Scénarios ayant déclenché C3

### 6. Performance
- Temps total, moyen, min, max

### 7. Conclusions et Recommandations
- Évaluation convergence
- Évaluation stabilité
- Évaluation inégalités
- **Configuration recommandée** (optimale)

## 💡 Conseils d'utilisation

### Pour tester rapidement une hypothèse

1. Modifier `test_experiment_small.py`
2. Définir 2-4 scénarios ciblés
3. Lancer : `python test_experiment_small.py`
4. Analyser le rapport

### Pour une étude systématique

1. Définir la grille dans `experiment_grid.py`
2. Estimer le temps : ~0.15s × 120 cycles × N_scénarios
3. Lancer : `python -m iris.simulations.experiment_grid`
4. Générer le rapport
5. Analyser dans un notebook Jupyter

### Pour comparer deux configurations

```python
import pandas as pd

df = pd.read_csv('results/grid/summary.csv')

# Comparer deux scénarios spécifiques
s1 = df[df['scenario_name'] == 'N200_cata0_rho005_seed1_t600'].iloc[0]
s2 = df[df['scenario_name'] == 'N200_cata1_rho005_seed1_t600'].iloc[0]

print(f"Sans catastrophes: θ={s1['theta_mean']:.4f}, Gini={s1['gini_final']:.3f}")
print(f"Avec catastrophes: θ={s2['theta_mean']:.4f}, Gini={s2['gini_final']:.3f}")
```

## 🎓 Cas d'usage

### Étude de stabilité

**Question** : Le système est-il stable avec de grandes populations ?

```python
# Filtrer par population
large_pop = df[df['initial_agents'] >= 1000]
print(f"θ_std moyen (N≥1000): {large_pop['theta_std'].mean():.4f}")
```

### Effet des catastrophes

**Question** : Les catastrophes déstabilisent-elles le système ?

```python
with_cata = df[df['enable_catastrophes'] == True]
without_cata = df[df['enable_catastrophes'] == False]

diff_std = with_cata['theta_std'].mean() - without_cata['theta_std'].mean()
print(f"Différence θ_std: {diff_std:+.4f} ({diff_std/without_cata['theta_std'].mean()*100:+.1f}%)")
```

### Optimisation ρ

**Question** : Quel ρ minimise les inégalités ?

```python
by_rho = df.groupby('conservation_rate')['gini_final'].mean()
optimal_rho = by_rho.idxmin()
print(f"ρ optimal pour Gini minimal: {optimal_rho}")
```

## 📊 Métriques clés à surveiller

### Stabilité économique

- **θ_mean** ≈ 1.0 : Convergence vers équilibre
- **θ_std** < 0.05 : Faibles oscillations
- **C3_activations** = 0 : Pas de crise

### Équité sociale

- **Gini** < 0.4 : Faible inégalité
- **Gini** 0.4-0.6 : Inégalité modérée
- **Gini** > 0.6 : Forte inégalité

### Dynamique démographique

- **population_final / population_initial** : Croissance
- **births - deaths** : Solde naturel

### Efficacité de régulation

- **kappa_mean**, **eta_mean** ≈ 1.0 : Régulation neutre
- **C2_activations** faible : Peu d'interventions profondes

---

**Auteur** : Arnault Nolan
**Version** : 1.0
**Date** : 2025-11-22
