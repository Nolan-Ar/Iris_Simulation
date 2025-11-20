# Documentation des Figures - Pack Thèse IRIS

Ce document fournit les légendes détaillées et l'interprétation des figures standardisées générées pour illustrer le fonctionnement du système IRIS dans le cadre d'une thèse.

## Table des Matières

1. [Figure 1 – Paramètres de Régulation RAD](#figure-1--paramètres-de-régulation-rad)
2. [Figure 2 – Revenu Universel et Modulation](#figure-2--revenu-universel-et-modulation)
3. [Figure 3 – Valeur Vivante en Circulation](#figure-3--valeur-vivante-en-circulation)
4. [Figure 4 – Distribution de la Richesse et Inégalités](#figure-4--distribution-de-la-richesse-et-inégalités)
5. [Guide d'Utilisation](#guide-dutilisation)

---

## Figure 1 – Paramètres de Régulation RAD

### Fichier généré
`thesis_fig1_regulation_parameters.png`

### Description générale

Cette figure présente l'évolution temporelle des trois paramètres fondamentaux du Régulateur Automatique Décentralisé (RAD) du système IRIS. Elle démontre le mécanisme de régulation contracyclique qui maintient l'équilibre thermodynamique du système économique.

### Sous-figures

#### (a) Taux d'inflation/contraction r_ic

**Formule** : r_ic = d(θ)/dt

**Légende** : Évolution du taux d'inflation/contraction r_ic, mesurant la vitesse de variation du thermomètre θ = D/V_on.

**Interprétation** :
- **r_ic > 0** : Système en phase d'inflation thermodynamique (D augmente plus vite que V_on)
- **r_ic < 0** : Système en phase de contraction (D diminue ou V_on augmente)
- **r_ic ≈ 0** : Système proche de l'équilibre instantané

**Usage thèse** : Illustre la dynamique de court terme du système et permet d'identifier les périodes de tension économique (pics de r_ic) et de stabilisation (r_ic proche de 0).

#### (b) Coefficient de rendement combustion η

**Formule** : η = η(θ), avec η ∈ [0.5, 2.0]

**Légende** : Évolution du coefficient η (eta) qui module le rendement de la combustion S+U→V (production de valeur patrimoniale).

**Interprétation** :
- **η < 1** : Rendement réduit (freine la production) → appliqué en surchauffe (θ > 1)
- **η = 1** : Rendement nominal (équilibre) → système à l'équilibre (θ = 1)
- **η > 1** : Rendement augmenté (stimule la production) → appliqué en sous-régime (θ < 1)

**Mécanisme contracyclique** : Quand θ augmente (surchauffe), le RAD réduit η pour freiner la production et ramener θ vers 1. Inversement, quand θ diminue (sous-régime), η augmente pour stimuler la production.

**Usage thèse** : Démontre le premier levier de régulation du RAD agissant sur le côté "offre" (production de V).

#### (c) Coefficient de liquidité κ

**Formule** : κ = κ(θ), avec κ ∈ [0.5, 2.0]

**Légende** : Évolution du coefficient κ (kappa) qui module la liquidité du système par deux mécanismes : (1) conversion V→U : U = V × κ, et (2) distribution du RU : RU_t = κ × V_on × τ / N.

**Interprétation** :
- **κ < 1** : Liquidité réduite (freine l'injection monétaire) → appliqué en surchauffe (θ > 1)
- **κ = 1** : Liquidité nominale (équilibre) → système à l'équilibre (θ = 1)
- **κ > 1** : Liquidité augmentée (stimule l'injection monétaire) → appliqué en sous-régime (θ < 1)

**Mécanisme contracyclique** : κ est le **régulateur principal** de la liquidité. Il agit sur le côté "demande" en modulant à la fois les conversions de patrimoine en monnaie (V→U) et le montant du revenu universel distribué.

**Usage thèse** : Démontre le second levier de régulation du RAD, complémentaire à η, agissant sur le côté "demande" (injection de liquidité U).

### Message clé de la figure

**La régulation contracyclique du RAD maintient automatiquement le système proche de l'équilibre (θ ≈ 1) en ajustant simultanément η (production) et κ (liquidité) de manière inversement corrélée au thermomètre θ.**

---

## Figure 2 – Revenu Universel et Modulation

### Fichier généré
`thesis_fig2_universal_income.png`

### Description générale

Cette figure illustre le mécanisme de distribution du Revenu Universel (RU) dans IRIS et sa modulation par le coefficient κ selon la situation thermodynamique du système.

### Sous-figures

#### (a) Revenu Universel distribué par agent

**Formule** : RU_t = κ_t × V_on(t-1) × τ / N_agents

**Légende** : Évolution temporelle du montant de revenu universel (RU) distribué à chaque agent, exprimé en unités de monnaie U.

**Interprétation** :
- Le RU varie dans le temps en fonction de trois facteurs :
  1. **V_on** : La valeur vivante totale en circulation (patrimoine actif des agents)
  2. **κ_t** : Le coefficient de liquidité (modulation contracyclique)
  3. **τ** : Le taux de RU configuré (paramètre fixe, typiquement 1-2%)

**Observations attendues** :
- Tendance générale : Le RU suit l'évolution de V_on (croissance économique)
- Fluctuations : Modulées par κ selon la situation thermodynamique
- En surchauffe (θ > 1) : RU réduit par κ < 1 (refroidissement)
- En sous-régime (θ < 1) : RU augmenté par κ > 1 (réchauffement)

**Usage thèse** : Démontre que le RU n'est pas un montant fixe mais un mécanisme adaptatif qui contribue à la régulation thermodynamique tout en assurant un soutien de base aux agents.

#### (b) Modulation du RU par κ

**Légende** : Superposition du RU par agent (axe gauche, orange) et du coefficient κ (axe droit, vert) pour visualiser la corrélation entre les deux variables.

**Interprétation** :
- **Corrélation positive attendue** : Quand κ augmente, le RU augmente proportionnellement
- **Anti-corrélation avec θ** : Quand θ > 1 (surchauffe), κ diminue, donc RU diminue
- **Effet stabilisateur** : La modulation du RU par κ contribue à ramener θ vers 1

**Exemple concret** :
- Période de surchauffe : θ = 1.2 → κ = 0.85 → RU réduit de 15%
- Période de sous-régime : θ = 0.8 → κ = 1.15 → RU augmenté de 15%

**Usage thèse** : Illustre le rôle dual du RU : (1) soutien social universel, (2) outil de régulation macroéconomique contracyclique.

### Message clé de la figure

**Le RU dans IRIS n'est pas un simple transfert fixe, mais un mécanisme de régulation adaptatif modulé par κ qui contribue activement à la stabilité thermodynamique tout en garantissant un revenu de base à tous les agents.**

---

## Figure 3 – Valeur Vivante en Circulation

### Fichier généré
`thesis_fig3_circulating_value.png`

### Description générale

Cette figure présente l'évolution de V_on, la "valeur vivante" représentant le patrimoine actif des agents en circulation. V_on est la variable centrale utilisée pour calculer le thermomètre θ et le montant du RU.

### Sous-figures

#### (a) Évolution de la valeur vivante en circulation

**Définition** : V_on = Σ_i V_i (somme des patrimoines V de tous les agents vivants)

**Légende** : Évolution temporelle de V_on, la valeur totale en patrimoine (Verum) détenue par les agents actifs du système.

**Interprétation** :
- **Tendance croissante** : Croissance économique naturelle (production > dissipation)
- **Croissance démographique** : Si la population augmente, V_on augmente aussi
- **Fluctuations** : Reflètent les cycles de combustion (production S+U→V) et les chocs

**Distinction importante** :
- **V_on** : Patrimoine des agents vivants (base pour θ et RU)
- **V_total** : Inclut aussi les patrimoines des entreprises (V_entreprise, V_operationnel)

**Usage thèse** : Illustre la dynamique de croissance du patrimoine collectif et justifie l'indexation du RU sur V_on (le RU croît avec la richesse collective).

#### (b) Proportion de valeur active (V_on / V_total)

**Formule** : Ratio = V_on / (V_on + V_entreprises)

**Légende** : Proportion de la valeur totale du système qui est détenue par les agents (par opposition aux entreprises).

**Interprétation** :
- **Ratio élevé (>0.8)** : Majorité du patrimoine chez les agents (économie "populaire")
- **Ratio modéré (0.6-0.8)** : Équilibre entre agents et entreprises
- **Ratio faible (<0.6)** : Forte concentration du patrimoine dans les entreprises

**Observations attendues** :
- Ratio stable dans le temps → équilibre structurel préservé
- Oscillations légères → flux de combustion (V sort des entreprises vers les agents via salaires)

**Usage thèse** : Permet d'analyser la répartition structurelle du patrimoine entre agents et entreprises, et de vérifier que les mécanismes de distribution (salaires, RU) maintiennent un équilibre.

### Message clé de la figure

**V_on représente le patrimoine vivant en circulation et sert de base pour l'indexation du RU et le calcul du thermomètre. Son évolution reflète la dynamique de création de valeur et la croissance économique du système.**

---

## Figure 4 – Distribution de la Richesse et Inégalités

### Fichier généré
`thesis_fig4_wealth_distribution.png`

### Description générale

Cette figure analyse les inégalités de richesse dans le système IRIS à travers trois représentations complémentaires : l'évolution temporelle du Gini, la distribution finale des richesses, et la courbe de Lorenz.

### Sous-figures

#### (a) Évolution des inégalités dans le temps

**Métrique** : Coefficient de Gini G ∈ [0, 1]

**Légende** : Évolution temporelle du coefficient de Gini mesurant les inégalités de richesse (V_i) entre agents.

**Interprétation** :
- **G = 0** : Égalité parfaite (tous les agents ont la même richesse)
- **G = 1** : Inégalité maximale (un agent détient toute la richesse)
- **G ∈ [0.3, 0.4]** : Inégalités modérées (seuil acceptable dans les sociétés réelles)

**Observations attendues dans IRIS** :
- **Phase initiale** : Gini faible (distribution initiale relativement égale)
- **Tendance** : Légère augmentation naturelle (accumulation différenciée)
- **Stabilisation** : Grâce au RU et à la démographie (naissances/héritages)
- **Pas d'explosion** : Le RU empêche la divergence exponentielle des inégalités

**Seuils de référence** :
- Ligne verte (G = 0) : Égalité parfaite (irréaliste)
- Ligne orange (G = 0.4) : Seuil modéré (objectif du système IRIS)

**Usage thèse** : Démontre que le mécanisme de RU modulé par κ maintient les inégalités dans une fourchette acceptable sans les éliminer complètement (ce qui serait économiquement inefficace).

#### (b) Distribution finale de la richesse

**Représentation** : Histogramme des richesses V_i des agents en fin de simulation

**Légende** : Distribution de la richesse patrimoniale (V_i) entre les N agents du système à l'instant final.

**Interprétation** :
- **Forme de la distribution** :
  - **Log-normale** : Typique des systèmes économiques réels (quelques riches, beaucoup de moyens/pauvres)
  - **Bimodale** : Peut indiquer une stratification (classes sociales)
  - **Uniforme** : Indiquerait une égalisation excessive (non réaliste)

**Observations attendues** :
- Queue droite longue (fat tail) : Quelques agents très riches
- Mode vers la gauche : Majorité des agents avec richesse modérée
- Pas de "pic à zéro" : Le RU empêche l'appauvrissement total

**Usage thèse** : Visualise concrètement la répartition finale de la richesse et permet de valider que la distribution ressemble aux distributions réelles (log-normale).

#### (c) Courbe de Lorenz

**Définition** : Courbe représentant la proportion cumulée de richesse détenue par la proportion cumulée de population (classée du plus pauvre au plus riche).

**Légende** : Courbe de Lorenz comparée à la ligne d'égalité parfaite (diagonale). L'aire entre les deux courbes mesure visuellement le coefficient de Gini.

**Interprétation** :
- **Diagonale** : Égalité parfaite (Gini = 0)
- **Courbe en dessous** : Plus la courbe s'écarte, plus les inégalités sont fortes
- **Zone ombrée** : Aire proportionnelle au Gini (Gini = 2 × Aire)

**Lecture pratique** :
- Point (0.5, y) : Les 50% les plus pauvres détiennent y% de la richesse
- Si y = 0.3 : Les 50% les plus pauvres détiennent 30% → forte inégalité
- Si y = 0.5 : Les 50% les plus pauvres détiennent 50% → égalité parfaite

**Usage thèse** : Visualisation graphique élégante du niveau d'inégalité, complémentaire au Gini numérique. Permet de communiquer intuitivement le degré d'égalité/inégalité.

### Message clé de la figure

**Le système IRIS maintient les inégalités (Gini) dans une fourchette modérée grâce au RU, sans les supprimer complètement. La distribution finale ressemble aux distributions réelles (log-normale), validant le réalisme économique du modèle.**

---

## Guide d'Utilisation

### Comment générer le pack de figures ?

#### Dans le code Python

```python
from iris.analysis.iris_visualizer import IRISVisualizer
from iris.core.iris_scenarios import ScenarioRunner

# Exécuter un scénario
runner = ScenarioRunner(n_agents=100)
economy = runner.run_baseline_stable(steps=1200)  # 100 ans

# Générer le pack thèse
viz = IRISVisualizer(output_dir="thesis_figures")
viz.plot_thesis_pack(economy.history, scenario_name="baseline_stable")
```

#### Sortie attendue

Les 4 figures sont sauvegardées dans `thesis_figures/` :
- `thesis_fig1_regulation_parameters.png`
- `thesis_fig2_universal_income.png`
- `thesis_fig3_circulating_value.png`
- `thesis_fig4_wealth_distribution.png`

### Recommandations pour l'inclusion dans la thèse

#### Ordre de présentation

1. **Figure 3** (V_on) en premier : Introduit la variable de base
2. **Figure 1** (r, η, κ) ensuite : Montre les mécanismes de régulation
3. **Figure 2** (RU) après : Illustre un mécanisme concret (RU modulé)
4. **Figure 4** (Gini) en conclusion : Évalue l'impact social du système

#### Légendes minimales pour le document LaTeX

**Figure 1** :
> Évolution temporelle des paramètres de régulation du RAD : (a) taux d'inflation/contraction r_ic, (b) coefficient de rendement combustion η, (c) coefficient de liquidité κ. Les trois paramètres oscillent autour de leurs valeurs d'équilibre (0, 1, 1) et s'ajustent de manière contracyclique pour maintenir θ ≈ 1.

**Figure 2** :
> Revenu universel par agent et sa modulation par κ : (a) évolution du montant distribué, (b) corrélation avec le coefficient κ. Le RU suit la formule RU_t = κ_t × V_on × τ / N, montrant l'adaptation contracyclique du revenu aux conditions économiques.

**Figure 3** :
> Valeur vivante en circulation (V_on) : (a) évolution temporelle du patrimoine total des agents, (b) proportion de V_on dans la valeur totale du système. V_on sert de base au calcul du thermomètre θ et à l'indexation du RU.

**Figure 4** :
> Distribution de la richesse et inégalités : (a) évolution du coefficient de Gini dans le temps, (b) histogramme de la distribution finale des richesses, (c) courbe de Lorenz. Le système maintient les inégalités à un niveau modéré (Gini ≈ 0.3-0.4) grâce au mécanisme de RU.

### Scénarios recommandés pour les figures

| Scénario | Objectif | Intérêt pour la thèse |
|----------|----------|-----------------------|
| `baseline_stable` | Équilibre stable long terme | Démontre la stabilité naturelle du système |
| `regulation_only` | Régulation pure (sans modules) | Isole les mécanismes de régulation RAD |
| `crisis_high_volatility` | Stress test extrême | Démontre la résilience du RAD |
| `no_regulation` (témoin) | Sans RAD (κ=η=1 fixes) | Contraste avec système non régulé |

### Checklist avant génération

- [ ] Vérifier que l'historique contient les variables nécessaires :
  - `time`, `kappa`, `eta`, `r_ic`
  - `thermometer`, `indicator`
  - `gini_coefficient`
  - `V_on` ou `total_V`
  - Optionnels : `RU_per_capita`, `wealth_distribution`

- [ ] Durée de simulation suffisante (minimum 100 steps = ~8 ans)
- [ ] Module RU activé (`universal_income_rate > 0`)
- [ ] Résolution d'image appropriée (300 dpi par défaut)

### Personnalisation avancée

Pour modifier le style des figures, éditer `iris_visualizer.py` :

```python
# Couleurs personnalisées
colors = {
    'r_ic': '#E63946',    # Rouge
    'eta': '#9D4EDD',     # Violet
    'kappa': '#06A77D',   # Vert
    'RU': '#F18F01',      # Orange
    'V_on': '#2E86AB',    # Bleu
    'Gini': '#D62828',    # Rouge foncé
}

# Taille de police
plt.rcParams['font.size'] = 12  # Augmenter pour meilleure lisibilité

# Format de sortie
output_path = self.output_dir / "fig1.pdf"  # PDF au lieu de PNG
```

---

## Références Théoriques

### Thermomètre θ
- **Définition** : θ = D / V_on
- **Interprétation** : Mesure de la tension thermodynamique du système
- **Équilibre** : θ = 1 (demande = offre potentielle)

### Régulation contracyclique
- **Principe** : κ et η varient inversement à θ pour ramener le système vers l'équilibre
- **Formules** : κ = 1 - β×(θ-1), η = 1 - α×(θ-1)
- **Bornes** : κ, η ∈ [0.5, 2.0]

### Revenu Universel IRIS
- **Formule** : RU_t = κ_t × V_on(t-1) × τ / N_agents
- **Spécificité** : Indexé sur V_on (croît avec la richesse collective)
- **Modulation** : Par κ selon la situation thermodynamique

### Coefficient de Gini
- **Définition** : G = 2 × Aire(Lorenz ↔ Égalité)
- **Plage** : G ∈ [0, 1]
- **Objectif IRIS** : Maintenir G ∈ [0.3, 0.4] (inégalités modérées)

---

## Interprétation Globale du Pack

### Ce que montrent les 4 figures ensemble

1. **Cohérence thermodynamique** (Fig. 1) : Les paramètres de régulation oscillent de manière contracyclique autour de leurs valeurs d'équilibre

2. **Mécanisme adaptatif du RU** (Fig. 2) : Le RU n'est pas fixe mais modulé par κ, contribuant activement à la stabilité

3. **Croissance économique** (Fig. 3) : V_on croît dans le temps, démontrant que le système est productif (création de valeur)

4. **Équité sociale** (Fig. 4) : Les inégalités restent modérées malgré l'absence de redistribution forcée (hors RU)

### Message global pour la thèse

> **Le système IRIS maintient simultanément trois propriétés souhaitables : (1) stabilité thermodynamique (θ ≈ 1), (2) croissance économique (V_on croissant), (3) équité sociale modérée (Gini < 0.4), grâce à la régulation contracyclique automatique du RAD et au mécanisme de RU adaptatif.**

---

## Notes Techniques

### Données requises dans l'historique

Pour générer l'ensemble du pack, l'historique doit contenir :

```python
history = {
    'time': [...],              # Obligatoire
    'kappa': [...],             # Obligatoire
    'eta': [...],               # Obligatoire (si disponible)
    'r_ic': [...],              # Obligatoire (si disponible)
    'thermometer': [...],       # Obligatoire
    'indicator': [...],         # Obligatoire
    'gini_coefficient': [...],  # Obligatoire
    'V_on': [...],              # Recommandé (sinon utilise total_V)
    'total_V': [...],           # Fallback pour V_on
    'RU_per_capita': [...],     # Optionnel (pour Fig. 2)
    'wealth_distribution': [...], # Optionnel (pour Fig. 4b et 4c)
    'population': [...]         # Optionnel
}
```

### Gestion des données manquantes

Les fonctions de visualisation gèrent gracieusement les données manquantes :
- Si `r_ic` manque : Tracé à 0 avec message
- Si `eta` manque : Utilise valeur fixe à 1.0
- Si `RU_per_capita` manque : Affiche message d'avertissement
- Si `wealth_distribution` manque : Affiche placeholders pour histogramme et Lorenz

### Performance

Temps de génération typique (1000 steps, 100 agents) :
- Figure 1 : ~2 secondes
- Figure 2 : ~2 secondes
- Figure 3 : ~2 secondes
- Figure 4 : ~3 secondes (courbe de Lorenz)
- **Total** : ~10 secondes

---

**Auteur** : Arnault Nolan
**Date** : 2025
**Version** : 1.0
