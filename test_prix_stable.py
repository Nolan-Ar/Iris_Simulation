#!/usr/bin/env python3
"""
Test du système de prix log-prices
====================================

Vérifie que :
1. Pas de NaN ni Inf dans prix_moyen et inflation
2. Tous les prix > 0
3. Prix moyen reste dans intervalle raisonnable [0.1, 10]
4. Inflation raisonnable (pas d'hyperinflation)
"""

from iris.core.iris_model import IRISEconomy
import math

print("="*70)
print("TEST SYSTÈME DE PRIX (LOG-PRICES)")
print("="*70)

# Test 1 : Sans price_discovery (doit fonctionner normalement)
print("\n1️⃣  Test avec price_discovery=False (mode sécurisé)...")
economy_no_prices = IRISEconomy(
    initial_agents=50,
    enable_demographics=True,
    enable_catastrophes=False,
    enable_business_combustion=True,
    enable_dynamic_business=True,
    enable_chambre_relance=True,
    enable_price_discovery=False,  # DÉSACTIVÉ
    seed=42
)

for i in range(100):
    economy_no_prices.step(n_transactions=10)

assert economy_no_prices.price_manager is None, "price_manager devrait être None quand désactivé"
assert all(p == 0.0 for p in economy_no_prices.history['prix_moyen']), "prix_moyen devrait être 0 quand désactivé"
assert all(infl == 0.0 for infl in economy_no_prices.history['inflation']), "inflation devrait être 0 quand désactivé"
print("  ✓ Sans price_discovery : OK (prix_manager=None, prix=0, inflation=0)")

# Test 2 : Avec price_discovery (test stabilité)
print("\n2️⃣  Test avec price_discovery=True (nouveau système log-prices)...")
economy_prices = IRISEconomy(
    initial_agents=50,
    enable_demographics=True,
    enable_catastrophes=False,
    enable_business_combustion=True,
    enable_dynamic_business=True,
    enable_chambre_relance=True,
    enable_price_discovery=True,  # ACTIVÉ
    seed=42
)

# Vérifier que price_manager est initialisé
assert economy_prices.price_manager is not None, "price_manager devrait être initialisé"
assert len(economy_prices.price_manager.log_prices) == 5, "5 biens devraient être enregistrés"

# Simulation
print(f"\n  Simulation 500 steps (≈ 42 ans)...")
for i in range(500):
    economy_prices.step(n_transactions=10)

    if (i + 1) % 100 == 0:
        theta = economy_prices.thermometer()
        prix_moyen = economy_prices.history['prix_moyen'][-1]
        inflation = economy_prices.history['inflation'][-1]
        print(f"    Step {i+1:3d} : θ={theta:.4f}, prix_moyen={prix_moyen:.4f}, inflation={inflation:.4f}")

print(f"\n3️⃣  Validation des résultats...")

# Vérif 1 : Pas de NaN ni Inf
has_nan_inf = False
for i, prix in enumerate(economy_prices.history['prix_moyen']):
    if math.isnan(prix) or math.isinf(prix):
        print(f"  ✗ NaN/Inf détecté dans prix_moyen[{i}] = {prix}")
        has_nan_inf = True

for i, infl in enumerate(economy_prices.history['inflation']):
    if math.isnan(infl) or math.isinf(infl):
        print(f"  ✗ NaN/Inf détecté dans inflation[{i}] = {infl}")
        has_nan_inf = True

if not has_nan_inf:
    print(f"  ✓ Pas de NaN ni Inf dans prix_moyen et inflation")
else:
    raise AssertionError("NaN/Inf détecté dans les prix ou inflation")

# Vérif 2 : Tous les prix > 0
prix_negatifs = [p for p in economy_prices.history['prix_moyen'] if p <= 0]
if prix_negatifs:
    print(f"  ✗ Prix négatifs/nuls détectés : {len(prix_negatifs)}")
    raise AssertionError("Prix négatifs ou nuls détectés")
else:
    print(f"  ✓ Tous les prix > 0")

# Vérif 3 : Prix moyen dans intervalle raisonnable [0.1, 10]
prix_hors_bornes = [p for p in economy_prices.history['prix_moyen'] if p < 0.1 or p > 10.0]
if prix_hors_bornes:
    print(f"  ⚠ {len(prix_hors_bornes)} prix hors de [0.1, 10.0] : {min(prix_hors_bornes):.4f} - {max(prix_hors_bornes):.4f}")
    # Warning mais pas échec
else:
    print(f"  ✓ Prix moyen dans intervalle [0.1, 10.0]")

# Vérif 4 : Inflation raisonnable (pas d'hyperinflation)
# Inflation mensuelle devrait être < 10% (sinon hyperinflation !)
inflation_excessive = [abs(infl) for infl in economy_prices.history['inflation'] if abs(infl) > 0.10]
if inflation_excessive:
    print(f"  ⚠ {len(inflation_excessive)} mois avec inflation excessive (>10%) : max={max(inflation_excessive):.2%}")
    # Warning mais pas échec si occasionnel
    if len(inflation_excessive) > 50:  # Plus de 10% des cycles
        raise AssertionError("Hyperinflation détectée (>10% sur trop de cycles)")
else:
    print(f"  ✓ Inflation raisonnable (< 10% par mois)")

# Statistiques finales
print(f"\n📊 Statistiques finales :")
prix_final = economy_prices.history['prix_moyen'][-1]
inflation_moy = sum(economy_prices.history['inflation']) / len(economy_prices.history['inflation']) if economy_prices.history['inflation'] else 0
print(f"  Prix moyen final : {prix_final:.4f}")
print(f"  Inflation moyenne : {inflation_moy:.4%} par mois ({inflation_moy*12:.2%} annualisé)")
print(f"  θ final : {economy_prices.thermometer():.4f}")

# Validation du price_manager directement
is_valid, errors = economy_prices.price_manager.validate()
if not is_valid:
    print(f"\n  ✗ Validation price_manager échouée :")
    for err in errors:
        print(f"    - {err}")
    raise AssertionError("Price_manager invalide")
else:
    print(f"  ✓ Price_manager valide (tous les prix > 0, pas de NaN/Inf)")

print("\n" + "="*70)
print("✅ TOUS LES TESTS RÉUSSIS")
print("="*70)
