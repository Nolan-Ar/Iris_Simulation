# IRIS - Graphiques d'Analyse Automatiques

## 🎨 Vue d'ensemble

Le système IRIS génère maintenant **automatiquement** des graphiques d'analyse professionnels pour chaque grille d'expériences.

**Localisation** : `results/<experiment_name>/plots/`

**Formats** : PNG, 150 DPI, haute résolution

**Génération** : Automatique à la fin de chaque run d'expériences

## 📊 Types de graphiques générés

### 1. **overview.png** - Vue d'ensemble

Grille 2×2 avec :
- **Distribution θ moyen** : Histogramme avec cible θ=1
- **Distribution θ std** : Mesure de la stabilité
- **Distribution Gini** : Inégalités de richesse
- **Scatter θ vs Gini** : Coloré par stabilité

**Utilité** : Vision globale rapide des résultats

### 2. **population_effect.png** - Effet de la population

Grille 2×2 avec boxplots :
- **θ std par population** : Stabilité selon taille
- **θ mean par population** : Convergence selon taille
- **Gini par population** : Inégalités selon taille
- **Croissance démographique** : Population finale vs initiale

**Utilité** : Identifier la taille optimale de population

### 3. **catastrophes_effect.png** - Effet des catastrophes

Comparaison ON/OFF avec boxplots :
- **θ std** : Impact sur la stabilité
- **θ mean** : Impact sur la convergence
- **Gini** : Impact sur les inégalités
- **Population finale** : Impact démographique

**Utilité** : Mesurer la résilience du système

### 4. **conservation_effect.png** - Effet du taux ρ

Grille 2×2 analysant ρ (conservation RU) :
- **θ std par ρ** : Stabilité selon conservation
- **θ mean par ρ** : Convergence selon conservation
- **Gini par ρ** : Inégalités selon conservation
- **Tendances** : Évolution θ_std et Gini vs ρ

**Utilité** : Optimiser le paramètre de conservation

### 5. **convergence_stability.png** - Convergence vs Stabilité

Scatter plot coloré :
- **Axes** : θ mean (convergence) vs θ std (stabilité)
- **Couleur** : Gini (inégalités)
- **Zones** : Vert (excellente), Jaune (bonne), Rouge (faible)
- **Cible** : Ligne θ=1.0

**Utilité** : Identifier les configurations optimales visuellement

### 6. **metrics_distribution.png** - Distribution des métriques

Grille 3×2 avec histogrammes :
- θ mean, θ std
- Gini final
- Population finale
- κ moyen, η moyen

Chaque graphique affiche :
- Moyenne (ligne rouge)
- Médiane (ligne bleue)
- Statistiques

**Utilité** : Comprendre la dispersion des résultats

### 7. **correlation_matrix.png** - Matrice de corrélation

Heatmap des corrélations entre :
- θ mean, θ std
- Gini final
- Population finale
- Catastrophes total
- κ mean, η mean
- C2/C3 activations

**Valeurs** : -1 (anticorrélation) à +1 (corrélation)
**Couleurs** : Coolwarm (bleu → rouge)

**Utilité** : Identifier les relations entre métriques

### 8. **best_scenarios.png** - Top 5 scénarios stables

Grille 2×2 avec :
- **Barres θ std** : Top 5 plus stables
- **Barres θ mean** : Convergence des top 5
- **Barres Gini** : Inégalités des top 5
- **Tableau** : Comparatif détaillé

**Utilité** : Identifier rapidement les meilleures configurations

### 9. **duration_effect.png** - Effet de la durée (optionnel)

Si plusieurs durées testées :
- θ std, θ mean, Gini, population par durée
- Boxplots comparatifs

**Utilité** : Voir si les résultats convergent dans le temps

### 10. **heatmaps.png** - Heatmaps 2D (optionnel)

Si assez de données (≥9 scénarios) :
- **Heatmap 1** : Population × ρ → θ std
- **Heatmap 2** : Population × ρ → Gini

Avec valeurs dans les cellules.

**Utilité** : Explorer l'espace paramétrique en 2D

## 🚀 Utilisation

### Génération automatique

Les graphiques sont générés automatiquement lors de :

```bash
# Test rapide
python test_experiment_small.py
# → Graphiques dans results/test_grid/plots/

# Grille complète
python -m iris.simulations.experiment_grid
# → Graphiques dans results/grid/plots/
```

### Génération manuelle

Si vous avez déjà des résultats :

```bash
python -m iris.simulations.plot_analysis results/test_grid
```

### Vérification

```bash
ls -lh results/test_grid/plots/
# Devrait afficher 8-10 fichiers PNG
```

## 📈 Interprétation

### Stabilité (θ std)

- **< 0.02** : ✅ Excellente stabilité
- **0.02 - 0.05** : ✓ Bonne stabilité
- **> 0.05** : ⚠ Stabilité faible

### Convergence (θ mean)

- **|θ - 1| < 0.1** : ✅ Excellente convergence
- **|θ - 1| < 0.3** : ✓ Bonne convergence
- **|θ - 1| > 0.3** : ⚠ Convergence à améliorer

### Inégalités (Gini)

- **< 0.4** : ✅ Faible inégalité
- **0.4 - 0.6** : ✓ Inégalité modérée
- **> 0.6** : ⚠ Forte inégalité

## 🎯 Cas d'usage

### 1. Identifier la configuration optimale

1. Regarder **convergence_stability.png**
2. Points en bas à gauche (faible θ_std) + près de θ=1 = meilleurs
3. Vérifier couleur (Gini) pour équité

### 2. Comparer catastrophes ON/OFF

1. Regarder **catastrophes_effect.png**
2. Comparer les boxplots
3. Différence θ_std indique impact stabilité

### 3. Optimiser le taux ρ

1. Regarder **conservation_effect.png**
2. Tendances (subplot 4) montre évolution
3. Choisir ρ minimisant θ_std ou Gini selon objectif

### 4. Analyse de sensibilité

1. Regarder **correlation_matrix.png**
2. Identifier quels paramètres influencent θ_std
3. Ajuster en conséquence

## 🛠️ Personnalisation

### Modifier les graphiques

Éditer `iris/simulations/plot_analysis.py` :

```python
class IRISPlotAnalysis:
    def plot_overview(self):
        # Modifier cette méthode
        # Exemple : changer couleurs, bins, etc.
        ax.hist(data, bins=30, color='skyblue')  # Au lieu de 20
```

### Ajouter un nouveau graphique

```python
def plot_my_analysis(self) -> None:
    """Mon analyse personnalisée."""
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Votre code de visualisation ici
    ax.plot(self.df['theta_mean'], self.df['gini_final'])
    
    plt.tight_layout()
    output_path = self.plots_dir / "my_analysis.png"
    plt.savefig(output_path, dpi=150)
    plt.close(fig)

# Dans plot_all(), ajouter :
self.plot_my_analysis()
plots_generated.append("my_analysis.png")
```

## 📊 Exemples de résultats

### Test rapide (4 scénarios)

**Résultats visuels** :
- θ converge vers 1.0 (excellente convergence)
- θ_std < 0.02 (excellente stabilité)
- Catastrophes augmentent θ_std de 19%
- Population N=200 → 2× plus stable que N=100

### Observations graphiques

**overview.png** :
- Distribution θ_mean centrée sur 1.0
- Distribution θ_std très resserrée (0.01-0.02)

**convergence_stability.png** :
- Tous les points en zone verte (excellente)
- N=200 en bas (plus stable)

**catastrophes_effect.png** :
- Boxplot ON légèrement plus haut (moins stable)
- Impact modéré mais visible

## 🎨 Qualité visuelle

**Résolution** : 150 DPI (publication quality)

**Tailles** :
- overview.png : ~150 KB
- population_effect.png : ~130 KB
- correlation_matrix.png : ~150 KB
- convergence_stability.png : ~90 KB

**Formats** : PNG avec transparence

**Couleurs** :
- Palette seaborn professionnelle
- Contraste élevé pour lisibilité
- Colorblind-friendly (viridis, coolwarm)

## 💡 Conseils

1. **Toujours** regarder d'abord `overview.png` et `convergence_stability.png`
2. **Comparer** les effets avec les graphiques spécialisés
3. **Utiliser** correlation_matrix.png pour comprendre les relations
4. **Identifier** les configurations optimales avec best_scenarios.png
5. **Exporter** les PNG directement dans vos présentations/rapports

## 🔗 Ressources

- **Documentation** : `DOCUMENTATION.md` (section 11)
- **Guide expériences** : `EXPERIMENTS_GUIDE.md`
- **Code source** : `iris/simulations/plot_analysis.py`

---

**Auteur** : Arnault Nolan
**Version** : 1.0
**Date** : 2025-11-22
