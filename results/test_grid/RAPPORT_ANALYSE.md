# IRIS - Rapport d'Analyse des Expériences

**Date**: 2025-11-22 02:01:49
**Nombre d'expériences**: 4
**Source**: `results/test_grid/summary.csv`

---

## 1. Résumé Global

### 1.1 Statistiques générales

| Métrique | Moyenne | Écart-type | Min | Max |
|----------|---------|------------|-----|-----|
| θ (theta) moyen | 1.0011 | 0.0403 | 0.9807 | 1.0615 |
| θ écart-type | 0.0152 | 0.0035 | 0.0099 | 0.0173 |
| Gini final | 0.5596 | 0.0105 | 0.5518 | 0.5740 |
| Population finale | 146.0000 | 59.4250 | 114.0000 | 235.0000 |
| Catastrophes totales | 0.2500 | 0.5000 | 0.0000 | 1.0000 |

## 2. Analyse de la Convergence θ

### 2.1 Stabilité du thermomètre

**Scénarios les plus stables** (θ_std faible):

| Scénario | θ moyen | θ std | θ final |
|----------|---------|-------|---------|
| `N200_cata0_rho005_seed1_t120` | 1.0615 | 0.0099 | 1.0786 |
| `N100_cata0_rho005_seed1_t120` | 0.9811 | 0.0167 | 0.9502 |
| `N100_cata0_rho000_seed1_t120` | 0.9811 | 0.0167 | 0.9502 |
| `N100_cata1_rho005_seed1_t120` | 0.9807 | 0.0173 | 0.9511 |

**Scénarios les moins stables** (θ_std élevé):

| Scénario | θ moyen | θ std | θ final |
|----------|---------|-------|---------|
| `N100_cata1_rho005_seed1_t120` | 0.9807 | 0.0173 | 0.9511 |
| `N100_cata0_rho005_seed1_t120` | 0.9811 | 0.0167 | 0.9502 |
| `N100_cata0_rho000_seed1_t120` | 0.9811 | 0.0167 | 0.9502 |
| `N200_cata0_rho005_seed1_t120` | 1.0615 | 0.0099 | 1.0786 |

## 3. Effet des Paramètres

### 3.1 Impact des catastrophes

| Paramètre | Catastrophes ON | Catastrophes OFF | Différence |
|-----------|-----------------|------------------|------------|
| θ std | 0.0173 | 0.0145 | +0.0028 (+19.4%) |
| θ moyen | 0.9807 | 1.0079 | -0.0272 (-2.7%) |
| Gini final | 0.5606 | 0.5592 | +0.0014 (+0.2%) |
| Population finale | 121.0000 | 154.3333 | -33.3333 (-21.6%) |

**Observations**:
- Scénarios avec catastrophes: 1
- Scénarios sans catastrophes: 3
- Total catastrophes (scénarios ON): 1

### 3.2 Impact du taux de conservation ρ

| ρ | θ std | θ moyen | Gini final | Pop finale |
|---|-------|---------|------------|------------|
| 0.00 | 0.0167 | 0.9811 | 0.5518 | 114 |
| 0.05 | 0.0146 | 1.0078 | 0.5621 | 157 |

**Interprétation**:
- ρ = 0.0 : RU maximum (100% de V disponible)
- ρ = 0.05 : RU standard (95% de V disponible)
- ρ = 0.15 : RU réduit (85% de V disponible)

### 3.3 Impact de la population initiale

| Pop. initiale | θ std | θ moyen | Gini final | Pop finale moyenne |
|---------------|-------|---------|------------|--------------------|
| 100 | 0.0169 | 0.9809 | 0.5548 | 116 |
| 200 | 0.0099 | 1.0615 | 0.5740 | 235 |

## 4. Analyse des Inégalités (Gini)

**Scénarios les plus égalitaires** (Gini faible):

| Scénario | Gini final | θ moyen | Pop. finale |
|----------|-----------|---------|-------------|
| `N100_cata0_rho005_seed1_t120` | 0.5518 | 0.9811 | 114 |
| `N100_cata0_rho000_seed1_t120` | 0.5518 | 0.9811 | 114 |
| `N100_cata1_rho005_seed1_t120` | 0.5606 | 0.9807 | 121 |
| `N200_cata0_rho005_seed1_t120` | 0.5740 | 1.0615 | 235 |

**Scénarios les plus inégalitaires** (Gini élevé):

| Scénario | Gini final | θ moyen | Pop. finale |
|----------|-----------|---------|-------------|
| `N200_cata0_rho005_seed1_t120` | 0.5740 | 1.0615 | 235 |
| `N100_cata1_rho005_seed1_t120` | 0.5606 | 0.9807 | 121 |
| `N100_cata0_rho005_seed1_t120` | 0.5518 | 0.9811 | 114 |
| `N100_cata0_rho000_seed1_t120` | 0.5518 | 0.9811 | 114 |

## 5. Activations de Régulation (C2/C3)

- **Total activations C2** (régulation profonde): 0
- **Total activations C3** (urgence): 0

✅ **Aucun scénario n'a déclenché C3** - Système stable

## 6. Performance des Simulations

- **Temps total**: 0.6s (0.0 min)
- **Temps moyen par simulation**: 0.15s
- **Temps le plus rapide**: 0.13s
- **Temps le plus long**: 0.20s

## 7. Conclusions et Recommandations

### 7.1 Convergence du thermomètre
✅ **Excellente convergence**: θ moyen = 1.0011 (écart: 0.0011)
✅ **Excellente stabilité**: θ std moyen = 0.0152

### 7.2 Inégalités de richesse
✓ **Inégalité modérée**: Gini moyen = 0.5596

### 7.3 Recommandations

**Configuration recommandée** (stabilité optimale):
- Scénario: `N200_cata0_rho005_seed1_t120`
- Population initiale: 200
- Catastrophes: OFF
- ρ (conservation): 0.05
- Résultats: θ=1.0615 ± 0.0099, Gini=0.5740

---

*Rapport généré automatiquement par `iris.simulations.generate_report`*
