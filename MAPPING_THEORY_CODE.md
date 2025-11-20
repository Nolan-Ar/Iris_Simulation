# Mapping Théorie ↔ Code IRIS

Ce document établit la correspondance entre les symboles théoriques du système IRIS et leur implémentation dans le code.

## Échelle Temporelle

**CONVENTION : 1 step = 1 mois**

- Constante globale : `STEPS_PER_YEAR = 12` (définie dans `iris_model.py`)
- Toutes les fréquences sont exprimées en mois (steps)
- Les mécanismes annuels sont déclenchés tous les 12 steps

### Fréquences des Mécanismes

| Mécanisme | Fréquence (steps) | Fréquence (années) | Code |
|-----------|-------------------|-------------------|------|
| **Combustion entreprises** | Chaque step (1) | 12 fois/an | `step()` - production mensuelle |
| **Revenu Universel (RU)** | Tous les 12 steps | 1 fois/an | `if self.time % STEPS_PER_YEAR == 0` |
| **Démographie** (naissances/décès) | Tous les 12 steps | 1 fois/an | `if self.time % STEPS_PER_YEAR == 0` |
| **Chambre de Relance** | Tous les 12 steps | 1 fois/an | `if self.time % STEPS_PER_YEAR == 0` |
| **Catastrophes** | Tous les 12 steps | 1 fois/an | `if self.time % STEPS_PER_YEAR == 0` |
| **Régulation RAD C2** | Tous les 12 steps | 1 fois/an | `T_period = 12` |
| **Calibration auto** | Tous les 50 steps | ~4 ans | `calibration_period = 50` |
| **Amortissement D** | Chaque step (1) | 12 fois/an | δ_m = 0.104%/mois appliqué |

### Exemple d'Utilisation

```python
from iris.core.iris_model import IRISEconomy, STEPS_PER_YEAR

# Créer l'économie
economy = IRISEconomy(initial_agents=100)

# Simuler 10 ans = 120 mois = 120 steps
economy.simulate(steps=10 * STEPS_PER_YEAR)  # 120 steps
```

## Variables d'État Macro

| Symbole Théorique | Signification | Variable/Attribut Code | Fichier + Fonction |
|-------------------|---------------|------------------------|-------------------|
| **V** | Verum - Patrimoine ancré, mémoire de valeur | `Agent.V_balance` | `iris_model.py::Agent` |
| **U** | Usage - Monnaie d'usage, liquidité | `Agent.U_balance` | `iris_model.py::Agent` |
| **S** | Service - Travail/service dans combustion | Paramètre implicite dans combustion | `iris_comptes_entreprises.py::distribute_V_genere()` |
| **V_on** | Valeur vivante en circulation (patrimoine actif des agents) | `get_V_on()` | `iris_model.py::IRISEconomy.get_V_on()` |
| **D** | Dette thermométrique totale (miroir de régulation) | `RADState.total_D()` | `iris_rad.py::RADState.total_D()`, `iris_model.py::RADState.total_D()` |
| **D_materielle** | Composante matérielle de D (biens physiques) | `RADState.D_materielle` | `iris_rad.py::RADState`, mis à jour dans `iris_model.py::_initialize_agents_object()` |
| **D_contractuelle** | Composante contractuelle de D (NFT financiers) | `RADState.D_contractuelle` | `iris_rad.py::RADState`, mis à jour via `iris_comptes_entreprises.py` |
| **D_consommation** | Composante consommation de D (démographie) | `RADState.D_consommation` | `iris_rad.py::RADState.add_D_consommation()` |
| **D_catastrophes** | Composante catastrophes de D (destructions) | `RADState.D_catastrophes` | `iris_rad.py::RADState.add_D_catastrophes()` |
| **D_services** | Composante services de D (flux d'entretien) | `RADState.D_services` | `iris_model.py::RADState.D_services` |
| **D_engagement** | Composante engagement de D (staking) | `RADState.D_engagement` | `iris_model.py::RADState.D_engagement` |
| **D_regulatrice** | Composante régulatrice de D (Chambre de Relance) | `RADState.D_regulatrice` | `iris_model.py::RADState.D_regulatrice` |

## Thermomètre et Indicateurs de Régulation

| Symbole Théorique | Signification | Variable/Attribut Code | Fichier + Fonction |
|-------------------|---------------|------------------------|-------------------|
| **θ** (theta) | Thermomètre économique = D / V_on | `thermometer()` | `iris_model.py::IRISEconomy.thermometer()` |
| **I** | Indicateur centré = θ - 1 | `indicator()` | `iris_model.py::IRISEconomy.indicator()` |
| **r_ic** | Taux inflation/contraction (variation de θ) | `RADState.r_ic` | `iris_rad.py::RADState.calculate_r_ic()`, `iris_model.py::RADState.calculate_r_ic()` |
| **ν_eff** (nu_eff) | Vélocité effective de circulation = U / V_on | `RADState.nu_eff` | `iris_rad.py::RADState.calculate_nu_eff()`, `iris_model.py::RADState.calculate_nu_eff()` |
| **τ_eng** (tau_eng) | Taux d'engagement = D_engagement / D_total | `RADState.tau_eng` | `iris_model.py::RADState.calculate_tau_eng()` |

## Paramètres de Régulation RAD

| Symbole Théorique | Signification | Variable/Attribut Code | Fichier + Fonction |
|-------------------|---------------|------------------------|-------------------|
| **κ** (kappa) | **Coefficient de liquidité** (contracyclique) - Module la conversion V→U ET le montant de RU distribué | `RADState.kappa` | `iris_rad.py::RADState.update_kappa()`, `iris_model.py::RADState.update_kappa()` |
| **η** (eta) | Coefficient rendement combustion S+U→V (contracyclique) | `RADState.eta` | `iris_rad.py::RADState`, `iris_model.py::IRISEconomy.compute_eta()` |
| **δ_m** (delta_m) | Amortissement mensuel de D (≈ 0.104%/mois ≈ 1.25%/an) | `RADState.delta_m` | `iris_rad.py::RADState.delta_m`, `iris_rad.py::RADState.apply_amortization()` |
| **τ** (tau) | Taux de revenu universel (1% par défaut) | `universal_income_rate` | `iris_model.py::IRISEconomy.universal_income_rate` |
| **α_RU** (alpha_RU) | Contrainte variation max RU (10% par défaut) | `alpha_RU` | `iris_model.py::IRISEconomy.alpha_RU` |
| **κ_min, κ_max** | Bornes de kappa [0.5, 2.0] | `RADState.kappa_min`, `RADState.kappa_max` | `iris_rad.py::RADState`, `iris_model.py::RADState` |
| **η_min, η_max** | Bornes de eta [0.5, 2.0] | `RADState.eta_min`, `RADState.eta_max` | `iris_rad.py::RADState`, `iris_model.py::RADState` |
| **β** (kappa_beta) | Sensibilité de κ à l'indicateur I | `RADState.kappa_beta` | `iris_rad.py::RADState.compute_kappa_target()` |
| **α** (eta_alpha) | Sensibilité de η à l'indicateur I | `RADState.eta_alpha` | `iris_rad.py::RADState.compute_eta_target()` |

### Rôle Central de κ (Coefficient de Liquidité)

**κ (kappa) est le régulateur PRINCIPAL de la liquidité dans IRIS**

κ intervient dans DEUX mécanismes fondamentaux :

1. **Conversion V→U (liquidation de patrimoine)** :
   - Formule : `U = V × κ`
   - Fichier : `iris_model.py::convert_V_to_U()`
   - Ligne ~1423

2. **Distribution du Revenu Universel (injection de liquidité)** :
   - Formule : `RU_t = κ_t × (V_on × τ) / N_agents`
   - Fichier : `iris_model.py::distribute_universal_income()`
   - Ligne ~1558

**Mécanisme Contracyclique** :

| Situation | θ | κ | Effet sur liquidité |
|-----------|---|---|-------------------|
| **Équilibre** | θ = 1.0 | κ = 1.0 | Liquidité nominale (neutre) |
| **Surchauffe** | θ > 1.0 | κ < 1.0 | FREINE : RU réduit + conversion V→U défavorable |
| **Sous-régime** | θ < 1.0 | κ > 1.0 | STIMULE : RU augmenté + conversion V→U favorable |

**Exemples Concrets** :

- Si θ = 1.2 (surchauffe +20%) → κ ≈ 0.85 :
  - Conversion : 100 V → 85 U (au lieu de 100 U)
  - RU : 85 U par agent (au lieu de 100 U)
  - **Effet : Refroidissement par réduction de liquidité**

- Si θ = 0.8 (sous-régime -20%) → κ ≈ 1.15 :
  - Conversion : 100 V → 115 U (au lieu de 100 U)
  - RU : 115 U par agent (au lieu de 100 U)
  - **Effet : Réchauffement par augmentation de liquidité**

## Flux et Mécanismes Économiques

| Symbole Théorique | Signification | Variable/Attribut Code | Fichier + Fonction |
|-------------------|---------------|------------------------|-------------------|
| **RU_t** | Revenu universel au cycle t = **κ_t** × (V_on × τ) / N_agents - **Modulé par κ (liquidité contracyclique)** | `distribute_universal_income()` | `iris_model.py::IRISEconomy.distribute_universal_income()` |
| **Combustion: S+U→V** | Génération de valeur par combustion | `distribute_V_genere()` | `iris_comptes_entreprises.py::CompteEntreprise.distribute_V_genere()` |
| **Conversion V→U** | Activation patrimoine en liquidité: U = V × **κ** - **κ module la liquidité** | `convert_V_to_U()` | `iris_model.py::IRISEconomy.convert_V_to_U()` |
| **Masse salariale** | 40% du V généré → U (salaires collaborateurs) | `ratio_salarial` (0.40) | `iris_comptes_entreprises.py::CompteEntreprise.distribute_V_genere()` |
| **Trésorerie** | 60% du V généré → V_operationnel (entreprise) | `ratio_tresorerie` (0.60) | `iris_comptes_entreprises.py::CompteEntreprise.distribute_V_genere()` |

## Comptes Entreprises

| Symbole Théorique | Signification | Variable/Attribut Code | Fichier + Fonction |
|-------------------|---------------|------------------------|-------------------|
| **V_entreprise** | Patrimoine de base de l'entreprise | `CompteEntreprise.V_entreprise` | `iris_comptes_entreprises.py::CompteEntreprise` |
| **V_operationnel** | Trésorerie opérationnelle (limitée) | `CompteEntreprise.V_operationnel` | `iris_comptes_entreprises.py::CompteEntreprise` |
| **NFT_financier** | Titre productif (excédent V converti) | `NFTFinancier` | `iris_comptes_entreprises.py::NFTFinancier` |
| **Seuil rétention** | Limite V_operationnel (20% × V_entreprise) | `CompteEntreprise.seuil_retention` | `iris_comptes_entreprises.py::CompteEntreprise.get_limite_retention()` |

## Démographie

| Symbole Théorique | Signification | Variable/Attribut Code | Fichier + Fonction |
|-------------------|---------------|------------------------|-------------------|
| **N_agents** | Nombre d'agents (population) | `len(agents)` | `iris_model.py::IRISEconomy.agents` |
| **âge moyen** | Âge moyen de la population | `age_moyen` | `iris_demographics.py::Demographics.get_statistics()` |
| **Taux natalité** | Taux de naissances annuel (4.14% par défaut) | `Demographics.birth_rate` | `iris_demographics.py::Demographics.process_births()` |
| **Espérance de vie** | Espérance de vie (80 ans par défaut) | `Demographics.life_expectancy` | `iris_demographics.py::Demographics` |
| **D_consommation_annuelle** | D de consommation par an et par personne | `Demographics.consumption_D_per_year` | `iris_demographics.py::Demographics` |

## Entreprises Dynamiques

| Symbole Théorique | Signification | Variable/Attribut Code | Fichier + Fonction |
|-------------------|---------------|------------------------|-------------------|
| **Taux création** | Taux création entreprises (5% par défaut) | `EntrepriseManager.taux_creation` | `iris_entreprises.py::EntrepriseManager.simulate_creations()` |
| **Taux faillite** | Taux faillite de base (3% par défaut) | `EntrepriseManager.taux_faillite_base` | `iris_entreprises.py::EntrepriseManager` |
| **Cycles avant faillite** | Cycles de déficit avant faillite (12 = 1 an) | `EntrepriseManager.cycles_avant_faillite` | `iris_entreprises.py::EntrepriseManager.check_faillites()` |
| **Seuil rentabilité** | V minimum à générer par cycle | `EntrepriseManager.seuil_rentabilite_base` | `iris_entreprises.py::EntrepriseManager` |

## Capteurs RAD et Couches de Régulation

| Symbole Théorique | Signification | Variable/Attribut Code | Fichier + Fonction |
|-------------------|---------------|------------------------|-------------------|
| **C1** | Couche 1: Régulation continue (chaque cycle) | Logique dans `regulate()` | `iris_model.py::IRISEconomy.regulate()` (lignes 1462-1473) |
| **C2** | Couche 2: Régulation profonde (tous les T=12 cycles) | `C2_activated` | `iris_model.py::IRISEconomy.regulate()` (lignes 1478-1486) |
| **C3** | Couche 3: Rebalancement d'urgence (si \|I\| > 30%) | `C3_activated` | `iris_model.py::IRISEconomy.regulate()` (lignes 1489+) |
| **Seuil C2** | Activation C2 si \|I\| > 15% | `RADState.C2_activation_threshold` | `iris_model.py::RADState.C2_activation_threshold` |
| **Seuil C3** | Activation C3 si \|I\| > 30% | `RADState.C3_activation_threshold` | `iris_model.py::RADState.C3_activation_threshold` |
| **T_period** | Périodicité régulation profonde (12 cycles = 1 an) | `RADState.T_period` | `iris_model.py::RADState.T_period` |

## Prix et Inflation (si activé)

| Symbole Théorique | Signification | Variable/Attribut Code | Fichier + Fonction |
|-------------------|---------------|------------------------|-------------------|
| **Prix moyen** | Prix moyen pondéré (si enable_price_discovery) | `PriceManager.get_average_price()` | `iris_prix.py::PriceManager.get_average_price()` |
| **Taux inflation** | Variation du prix moyen | `PriceManager.get_inflation_rate()` | `iris_prix.py::PriceManager.get_inflation_rate()` |

## Oracle d'Initialisation

| Symbole Théorique | Signification | Variable/Attribut Code | Fichier + Fonction |
|-------------------|---------------|------------------------|-------------------|
| **φ_or** (phi_or) | Facteur or de zone (équivalent or local) | `Oracle.phi_or` | `iris_oracle.py::Oracle` |
| **V_0** | Verum d'initialisation = valeur_réelle × auth_factor | `Asset.V_initial` | `iris_model.py::Asset.__post_init__()` |
| **D_0** | Miroir thermométrique initial = V_0 | `Asset.D_initial` | `iris_model.py::Asset.__post_init__()` |
| **NFT fondateur** | Preuve cryptographique d'existence unique | `Asset.nft_hash` | `iris_oracle.py::Oracle.emit_asset()` |
| **auth_factor** | Facteur d'authentification (1.0 = officiel) | `Asset.auth_factor` | `iris_model.py::Asset` |

## Gini et Inégalités

| Symbole Théorique | Signification | Variable/Attribut Code | Fichier + Fonction |
|-------------------|---------------|------------------------|-------------------|
| **G** (Gini) | Coefficient de Gini (0 = égalité, 1 = inégalité max) | `gini_coefficient()` | `iris_model.py::IRISEconomy.gini_coefficient()` |

## Configuration des Modules (Flags Enable/Disable)

IRIS permet de désactiver sélectivement les modules pour simplifier les simulations ou isoler les mécanismes de régulation.

### Flags de Configuration

| Flag | Par défaut | Description | Désactive |
|------|-----------|-------------|-----------|
| `enable_demographics` | `True` | Active la démographie | Naissances, décès, vieillissement, héritage |
| `enable_catastrophes` | `True` | Active les catastrophes | Chocs aléatoires (tremblements de terre, crises, etc.) |
| `enable_price_discovery` | `True` | Active les prix dynamiques | Mécanisme de prix explicites, inflation |
| `enable_dynamic_business` | `True` | Active entreprises dynamiques | Créations/faillites d'entreprises |
| `enable_business_combustion` | `True` | Active combustion entreprises | Production S+U→V, distribution 40/60 |
| `enable_chambre_relance` | `True` | Active Chambre de Relance | Redistribution pool orphelins |

### Mode "Regulation Only" (Pour Illustration Théorique)

**Objectif** : Illustrer uniquement les mécanismes de régulation contracyclique pour un chapitre de thèse, sans la complexité des modules annexes.

**Fichier** : `iris_scenarios.py::ScenarioRunner.run_regulation_only()`

**Configuration** :
```python
economy = IRISEconomy(
    initial_agents=100,
    enable_demographics=False,        # ❌ Pas de naissances/décès
    enable_catastrophes=False,        # ❌ Pas de chocs aléatoires
    enable_price_discovery=False,     # ❌ Pas de prix dynamiques
    enable_dynamic_business=False,    # ❌ Pas de créations/faillites
    enable_business_combustion=False, # ❌ Pas de production entreprise
    enable_chambre_relance=False,     # ❌ Pas de redistribution CR
)
```

**Modules Actifs (uniquement)** :
- ✅ Variables fondamentales : V, U, D
- ✅ Thermomètre : θ = D / V_on
- ✅ Régulateurs : κ (liquidité), η (production)
- ✅ Revenu Universel : RU = κ × (V_on × τ) / N
- ✅ Capteurs : r_ic (inflation), ν_eff (vélocité)
- ✅ Conversions V↔U
- ✅ Transactions U entre agents
- ✅ Couches RAD (C1, C2, C3)

**Mécanismes Démontrés** :
1. Régulation contracyclique par κ
2. Maintien de θ proche de 1 (équilibre thermodynamique)
3. Stabilisation sans modules externes

**Usage** :
```python
from iris.core.iris_scenarios import ScenarioRunner

runner = ScenarioRunner(n_agents=100)
economy = runner.run_regulation_only(steps=120)  # 10 ans = 120 mois
```

## Notes sur les Conventions

1. **Nomenclature θ (theta)** : Le thermomètre θ = D / V_on est LA métrique centrale du système IRIS. Il mesure la tension thermodynamique de l'économie.

2. **Contracyclicité** : Les paramètres κ et η sont **contracycliques** :
   - Surchauffe (θ > 1, I > 0) → κ ↓, η ↓ (freinent conversion et production)
   - Sous-régime (θ < 1, I < 0) → κ ↑, η ↑ (stimulent conversion et production)
   - Équilibre (θ = 1, I = 0) → κ = 1, η = 1 (neutre)

3. **Distribution organique 40/60** : Les entreprises distribuent le V généré par combustion selon :
   - 40% → Masse salariale (U, salaires collaborateurs)
   - 60% → Trésorerie (V_operationnel)

4. **Amortissement de D** : δ_m ≈ 0.104%/mois ≈ 1.25%/an (conforme théorie IRIS)

5. **V_on vs V_total** : V_on représente la **valeur vivante en circulation** (patrimoine actif des agents), utilisée pour le calcul du thermomètre θ et du RU.

6. **Revenu Universel** : RU_t = (V_on(t-1) × τ) / N_agents, avec contrainte de variation α_RU = 10%

7. **Couches de régulation** :
   - C1 : Continue (chaque cycle) - ajuste κ et η
   - C2 : Profonde (tous les 12 cycles) - si |I| > 15%
   - C3 : Urgence (si |I| > 30%) - rebalancement direct de D
