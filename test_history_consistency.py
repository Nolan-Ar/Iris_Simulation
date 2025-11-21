#!/usr/bin/env python3
"""
Test de cohérence de l'historique (ÉTAPE 7)
==========================================

Vérifie que le nouveau pipeline _snapshot_state() produit un historique cohérent :
1. Toutes les séries temporelles ont la même longueur
2. Les temps sont strictement croissants (0, 1, 2, ...)
3. Pas de NaN ni Inf dans les métriques clés
4. Les compteurs d'événements sont >= 0
"""

from iris.core.iris_model import IRISEconomy
import math

print("="*70)
print("TEST COHÉRENCE HISTORIQUE (ÉTAPE 7 - Pipeline _snapshot_state)")
print("="*70)

# Test avec configuration standard
print("\n1️⃣  Création économie de test (50 agents, 100 cycles)...")
economy = IRISEconomy(
    initial_agents=50,
    enable_demographics=True,
    enable_catastrophes=False,
    enable_business_combustion=True,
    enable_dynamic_business=True,
    enable_chambre_relance=True,
    enable_price_discovery=True,
    seed=42
)

# Simulation
n_steps = 100
print(f"   Simulation de {n_steps} steps...")
for i in range(n_steps):
    economy.step(n_transactions=10)
    if (i + 1) % 25 == 0:
        print(f"     Step {i+1}/{n_steps}")

print(f"\n2️⃣  Validation de la cohérence de l'historique...")

# Vérif 1 : Longueur cohérente
print(f"\n  📏 Vérification des longueurs...")
expected_length = n_steps
history_keys = list(economy.history.keys())
length_errors = []

for key in history_keys:
    actual_length = len(economy.history[key])
    if actual_length != expected_length:
        length_errors.append(f"{key}: {actual_length} != {expected_length}")

if length_errors:
    print(f"  ✗ Longueurs incohérentes détectées :")
    for err in length_errors:
        print(f"    - {err}")
    raise AssertionError("Longueurs d'historique incohérentes")
else:
    print(f"  ✓ Toutes les séries ont la longueur attendue : {expected_length}")

# Vérif 2 : Temps strictement croissant
print(f"\n  ⏰ Vérification de la séquence temporelle...")
time_sequence = economy.history['time']
expected_time_sequence = list(range(1, n_steps + 1))  # 1, 2, 3, ..., 100

if time_sequence != expected_time_sequence:
    print(f"  ✗ Séquence temporelle incorrecte :")
    print(f"    Attendu : {expected_time_sequence[:10]}... (premier 10)")
    print(f"    Obtenu  : {time_sequence[:10]}... (premier 10)")
    raise AssertionError("Séquence temporelle incorrecte")
else:
    print(f"  ✓ Temps strictement croissant : 1, 2, 3, ..., {n_steps}")

# Vérif 3 : Pas de NaN ni Inf dans les métriques clés
print(f"\n  🔢 Vérification des NaN/Inf...")
numeric_keys = ['total_V', 'total_U', 'total_D', 'thermometer', 'indicator',
                'kappa', 'eta', 'gini_coefficient', 'circulation_rate',
                'prix_moyen', 'inflation']

nan_inf_errors = []
for key in numeric_keys:
    if key in economy.history:
        for i, val in enumerate(economy.history[key]):
            if math.isnan(val) or math.isinf(val):
                nan_inf_errors.append(f"{key}[{i}] = {val}")

if nan_inf_errors:
    print(f"  ✗ NaN/Inf détectés :")
    for err in nan_inf_errors[:10]:  # Limite à 10 pour lisibilité
        print(f"    - {err}")
    raise AssertionError("NaN/Inf détectés dans l'historique")
else:
    print(f"  ✓ Pas de NaN ni Inf dans les métriques numériques")

# Vérif 4 : Compteurs d'événements >= 0
print(f"\n  📊 Vérification des compteurs d'événements...")
counter_keys = ['births', 'deaths', 'catastrophes', 'creations_entreprises',
                'faillites_entreprises', 'business_NFT_created']

negative_errors = []
for key in counter_keys:
    if key in economy.history:
        for i, val in enumerate(economy.history[key]):
            if val < 0:
                negative_errors.append(f"{key}[{i}] = {val}")

if negative_errors:
    print(f"  ✗ Compteurs négatifs détectés :")
    for err in negative_errors:
        print(f"    - {err}")
    raise AssertionError("Compteurs négatifs dans l'historique")
else:
    print(f"  ✓ Tous les compteurs >= 0")

# Vérif 5 : Cohérence population
print(f"\n  👥 Vérification de la cohérence démographique...")
population_errors = []
for i in range(len(economy.history['population'])):
    pop = economy.history['population'][i]
    if pop <= 0:
        population_errors.append(f"population[{i}] = {pop} <= 0")

if population_errors:
    print(f"  ✗ Population invalide :")
    for err in population_errors:
        print(f"    - {err}")
    raise AssertionError("Population invalide dans l'historique")
else:
    pop_min = min(economy.history['population'])
    pop_max = max(economy.history['population'])
    print(f"  ✓ Population valide : min={pop_min}, max={pop_max}")

# Statistiques finales
print(f"\n3️⃣  Statistiques finales...")
print(f"  Cycles simulés : {len(economy.history['time'])}")
print(f"  Temps final : {economy.history['time'][-1]}")
print(f"  Population finale : {economy.history['population'][-1]}")
print(f"  θ final : {economy.history['thermometer'][-1]:.4f}")
print(f"  Total naissances : {sum(economy.history['births'])}")
print(f"  Total décès : {sum(economy.history['deaths'])}")
print(f"  Variation population : {economy.history['population'][-1] - economy.history['population'][0]:+d}")

# Vérification des variables d'instance snapshot
print(f"\n4️⃣  Vérification des variables d'instance snapshot...")
snapshot_vars = ['_births_this_step', '_deaths_this_step', '_catastrophes_this_step',
                 '_business_masse_salariale', '_business_NFT_created',
                 '_C2_activated', '_C3_activated', '_D_lifetime_this_step',
                 '_creations_entreprises', '_faillites_entreprises']

missing_vars = []
for var in snapshot_vars:
    if not hasattr(economy, var):
        missing_vars.append(var)

if missing_vars:
    print(f"  ✗ Variables d'instance manquantes :")
    for var in missing_vars:
        print(f"    - {var}")
    raise AssertionError("Variables d'instance snapshot manquantes")
else:
    print(f"  ✓ Toutes les variables d'instance snapshot présentes ({len(snapshot_vars)} vars)")

print("\n" + "="*70)
print("✅ TOUS LES TESTS DE COHÉRENCE RÉUSSIS")
print("="*70)
print("\n🎉 Le pipeline _snapshot_state() produit un historique cohérent !")
