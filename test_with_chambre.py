#!/usr/bin/env python3
"""
Test avec Chambre de Relance activée pour stabiliser θ
"""
from iris.core.iris_model import IRISEconomy

print("="*70)
print("TEST AVEC CHAMBRE DE RELANCE ACTIVÉE")
print("="*70)

economy = IRISEconomy(
    initial_agents=100,
    enable_demographics=True,
    enable_catastrophes=False,
    enable_business_combustion=True,
    enable_dynamic_business=True,
    enable_chambre_relance=True,  # ACTIVÉ !
    seed=42
)

print(f"\n📊 État initial:")
print(f"  V total: {sum(a.V_balance for a in economy.agents.values()):.2f}")
print(f"  D total: {economy.rad.total_D():.2f}")
print(f"  θ: {economy.thermometer():.4f}")

print(f"\n⏳ Simulation 50 ans (600 mois)...")
print(f"\n{'Année':<6} {'θ':<8} {'κ':<8} {'η':<8} {'V total':<12} {'D total':<12} {'Pop':<6}")
print("-" * 70)

for i in range(600):
    economy.step(n_transactions=10)

    if (i + 1) % 120 == 0:  # Tous les 10 ans
        year = (i + 1) // 12
        V_total = sum(a.V_balance for a in economy.agents.values())
        D_total = economy.rad.total_D()
        theta = economy.thermometer()
        kappa = economy.rad.kappa
        eta = economy.rad.eta
        pop = len(economy.agents)

        print(f"{year:<6} {theta:<8.4f} {kappa:<8.4f} {eta:<8.4f} {V_total:<12.2f} {D_total:<12.2f} {pop:<6}")

print(f"\n📊 État final:")
V_final = sum(a.V_balance for a in economy.agents.values())
D_final = economy.rad.total_D()
theta_final = economy.thermometer()

print(f"  θ final: {theta_final:.4f} (cible: 1.0)")
print(f"  κ final: {economy.rad.kappa:.4f}")
print(f"  η final: {economy.rad.eta:.4f}")
print(f"  V total: {V_final:.2f}")
print(f"  D total: {D_final:.2f}")
print(f"  Population: {len(economy.agents)}")

print(f"\n📈 Composantes D:")
total_D = economy.rad.total_D()
print(f"  D_materielle:    {economy.rad.D_materielle:>10.2f} ({economy.rad.D_materielle/total_D*100:>5.1f}%)")
print(f"  D_services:      {economy.rad.D_services:>10.2f} ({economy.rad.D_services/total_D*100:>5.1f}%)")
print(f"  D_contractuelle: {economy.rad.D_contractuelle:>10.2f} ({economy.rad.D_contractuelle/total_D*100:>5.1f}%)")
print(f"  D_regulatrice:   {economy.rad.D_regulatrice:>10.2f} ({economy.rad.D_regulatrice/total_D*100:>5.1f}%)")

if abs(theta_final - 1.0) < 0.1:
    print(f"\n✓ SUCCÈS : θ = {theta_final:.4f} (dans la tolérance ±0.1)")
else:
    print(f"\n✗ ÉCHEC : θ = {theta_final:.4f} (hors tolérance)")

print("\n" + "="*70)
