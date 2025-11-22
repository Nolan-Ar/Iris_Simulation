# IRIS - Integrative Resilience Intelligence System

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

**IRIS** est un système économique thermodynamiquement cohérent qui simule une économie décentralisée avec régulation automatique. Le système maintient l'équilibre économique via un mécanisme cybernétique inspiré de la thermodynamique.

## 🎯 Vue d'ensemble

IRIS implémente une économie complète avec :

- **Monnaie vivante (V)** : Valeur productive en circulation
- **Revenu Universel (U)** : Distribution automatique périodique
- **Stipulat (S)** : Crédit productif pour les entreprises
- **Dette thermométrique (D)** : Miroir de la valeur pour la régulation
- **RAD (Régulateur Automatique Décentralisé)** : Thermostat économique

### Caractéristiques principales

✓ **Régulation automatique** via système tri-capteur (θ, ν_eff, τ_eng)
✓ **Algorithme antagoniste** entre κ (liquidité) et η (rendement)
✓ **Démographie dynamique** (naissances, décès, héritage)
✓ **Économie réelle** (entreprises, actifs, catastrophes)
✓ **Conservation thermodynamique** (V₀ = D₀, pas de création ex nihilo)
✓ **Chambre de Relance** pour recycler les actifs orphelins

## 🚀 Installation

```bash
# Cloner le dépôt
git clone https://github.com/Nolan-Ar/Iris_Simulation.git
cd Iris_Simulation

# Installer les dépendances
pip install -r requirements.txt
```

## 📖 Utilisation rapide

### Simulation basique

```python
from iris.core import IRISEconomy

# Créer une économie avec 100 agents
model = IRISEconomy(
    initial_agents=100,
    initial_total_wealth_V=100000.0,
    conservation_rate=0.05,  # Taux de conservation RU (ρ)
    enable_demographics=True,
    enable_catastrophes=True
)

# Simuler 120 cycles (10 ans, 1 cycle = 1 mois)
for t in range(120):
    model.step()

    # Afficher les indicateurs tous les 12 mois
    if t % 12 == 0:
        theta = model.thermometer()  # θ = D/V_on (cible: 1.0)
        print(f"Année {t//12}: θ={theta:.4f}, κ={model.rad.kappa:.4f}, η={model.rad.eta:.4f}")

# Obtenir les statistiques finales
stats = model.get_statistics()
print(f"Population finale: {stats['population']}")
print(f"V total: {stats['total_V']:.2f}")
print(f"U total: {stats['total_U']:.2f}")
```

### Test de l'antagonisme κ/η

```bash
# Exécuter le test de validation
python test_antagonism.py
```

Résultat attendu :
- θ converge vers 1.0 (écart < 0.3)
- κ et η varient différemment (antagonisme actif)
- Oscillations amorties et stables
- Respect des bornes [0.5, 2.0]

## 🏗️ Architecture

```
iris/
├── core/
│   ├── iris_model.py           # Modèle économique principal (IRISEconomy)
│   ├── iris_rad.py             # RAD - Régulateur Automatique Décentralisé
│   ├── iris_demographics.py    # Gestion population (naissances/décès)
│   ├── iris_catastrophes.py    # Événements catastrophiques
│   ├── iris_chambre_relance.py # Redistribution actifs orphelins
│   ├── iris_types.py           # Types de données (Agent, Asset, etc.)
│   └── __init__.py             # Exports publics
├── utils/
│   └── helpers.py              # Fonctions utilitaires
└── __init__.py
```

## 🔬 Concepts théoriques

### Le Thermomètre (θ)

```
θ = D / V_on
```

- **θ < 1** : Sous-investissement → Stimulation (κ↑, η↑)
- **θ = 1** : Équilibre parfait (cible du RAD)
- **θ > 1** : Surchauffe → Freinage (κ↓, η↓)

### Le RAD - Régulateur Automatique Décentralisé

Le RAD opère sur **3 couches** :

1. **C1 - Régulation continue** (chaque cycle)
   - Ajuste κ (coefficient V→U) via tri-capteur
   - Ajuste η (rendement S+U→V) avec antagonisme
   - Amortissement cyclique de D (δₘ ≈ 0.104%/mois)

2. **C2 - Régulation profonde** (tous les 12 mois)
   - Active si |I| > 15%
   - Recalibrage structurel

3. **C3 - Rebalancement d'urgence** (si |I| > 30%)
   - Intervention directe sur D_regulatrice
   - Mécanisme de dernier recours

### Système tri-capteur

Le RAD utilise **3 capteurs** pour réguler κ et η :

1. **r_t = θ** : Thermomètre (cible: 1.0)
2. **ν_eff = (U_burn + S_burn) / V_on** : Vélocité (cible: 0.20)
3. **τ_eng = U_stake / U_total** : Engagement (cible: 0.35)

### Formules de régulation

**Variation de κ** :
```
Δκ = α_κ×(ν_target - ν_eff) - β_κ×(τ_eng - τ_target) + γ_κ×(1 - θ)
```

**Variation de η** :
```
Δη = α_η×(1 - θ) + β_η×(ν_target - ν_eff) - γ_η×(τ_eng - τ_target)
```

**Antagonisme algorithmique** :
```
Si signe(Δκ) = signe(Δη) :
    Δη ← Δη × (1 - 0.3 × |Δκ|)
```

### Composantes de D (Dette thermométrique)

D n'est **pas** une dette juridique, c'est un indicateur de régulation :

- **D_materielle** : Biens et immobilisations
- **D_services** : Flux d'entretien (maintenance)
- **D_contractuelle** : Titres productifs (NFT financiers)
- **D_engagement** : Staking et mises en réserve
- **D_regulatrice** : Chambre de Relance (RU, redistribution)

## 📊 Indicateurs clés

| Indicateur | Formule | Cible | Description |
|------------|---------|-------|-------------|
| **θ (theta)** | D / V_on | 1.0 | Thermomètre économique |
| **I (indicator)** | θ - 1 | 0.0 | Écart à l'équilibre |
| **κ (kappa)** | - | 1.0 | Coefficient de liquidité [0.5, 2.0] |
| **η (eta)** | - | 1.0 | Rendement de combustion [0.5, 2.0] |
| **ν_eff** | (U_burn+S_burn)/V_on | 0.20 | Vélocité de circulation |
| **τ_eng** | U_stake/U_total | 0.35 | Taux d'engagement |

## 🧪 Tests

```bash
# Test de l'antagonisme κ/η
python test_antagonism.py

# Tests unitaires (à venir)
pytest tests/
```

## 📚 Documentation complète

Pour une documentation détaillée de l'architecture, des algorithmes et des formules théoriques, consultez :

- **[DOCUMENTATION.md](DOCUMENTATION.md)** : Architecture et fonctionnement détaillé
- **[Iris_proto_complet.md](Iris_proto_complet.md)** : Spécifications théoriques complètes

## 🔧 Configuration

Paramètres principaux du modèle :

```python
model = IRISEconomy(
    initial_agents=100,              # Nombre d'agents initial
    initial_total_wealth_V=100000.0, # Richesse totale initiale
    conservation_rate=0.05,          # ρ : taux conservation RU (0-0.3)
    w_S=0.5,                         # Poids Stipulat dans combustion
    w_U=0.5,                         # Poids U dans combustion
    enable_demographics=True,        # Activer démographie
    enable_catastrophes=True,        # Activer catastrophes
    enable_chambre_relance=True,     # Activer Chambre de Relance
    mode_population="object",        # "object" ou "vectorized"
    seed=42                          # Graine aléatoire (reproductibilité)
)
```

## 🎯 Roadmap

- [x] Système tri-capteur complet
- [x] Algorithme antagoniste κ/η
- [x] Démographie dynamique
- [x] Chambre de Relance
- [x] Tests de validation
- [ ] Interface graphique (dashboard)
- [ ] Export des données (CSV, JSON)
- [ ] Analyses statistiques avancées
- [ ] TAP/Staking réel (au-delà de l'algorithme)
- [ ] Documentation interactive

## 📄 Licence

Ce projet est sous licence MIT. Voir [LICENSE](LICENSE) pour plus de détails.

## 👨‍💻 Auteur

**Arnault Nolan**

## 🙏 Remerciements

Ce projet implémente la théorie économique IRIS développée dans les documents de recherche associés.

---

**Note** : IRIS est un système de recherche et d'expérimentation. Il ne constitue pas un conseil financier et ne doit pas être utilisé pour des décisions économiques réelles.
