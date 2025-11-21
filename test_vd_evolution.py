#!/usr/bin/env python3
"""
Test détaillé de l'évolution V/D pour diagnostiquer θ > 1
"""
from iris.core.iris_model import IRISEconomy

print("="*70)
print("DIAGNOSTIC DÉTAILLÉ : ÉVOLUTION V ET D")
print("="*70)

economy = IRISEconomy(
    initial_agents=100,
    enable_demographics=True,
    enable_catastrophes=False,
    enable_business_combustion=True,
    enable_dynamic_business=True,
    enable_chambre_relance=False,
    seed=42
)

print(f"\n📊 État initial:")
print(f"  V total: {sum(a.V_balance for a in economy.agents.values()):.2f}")
print(f"  D total: {economy.rad.total_D():.2f}")
print(f"  θ: {economy.thermometer():.4f}")
print(f"  Population: {len(economy.agents)}")

print(f"\n⏳ Simulation 50 ans (600 mois)...")
print(f"\n{'Année':<6} {'V total':<12} {'D total':<12} {'θ':<8} {'Pop':<6} {'D_mat':<10} {'D_srv':<10} {'D_ctr':<10} {'D_reg':<10}")
print("-" * 100)

for i in range(600):
    economy.step(n_transactions=10)

    if (i + 1) % 120 == 0:  # Tous les 10 ans
        year = (i + 1) // 12
        V_total = sum(a.V_balance for a in economy.agents.values())
        D_total = economy.rad.total_D()
        theta = economy.thermometer()
        pop = len(economy.agents)

        print(f"{year:<6} {V_total:<12.2f} {D_total:<12.2f} {theta:<8.4f} {pop:<6} "
              f"{economy.rad.D_materielle:<10.2f} {economy.rad.D_services:<10.2f} "
              f"{economy.rad.D_contractuelle:<10.2f} {economy.rad.D_regulatrice:<10.2f}")

print(f"\n📊 État final:")
print(f"  V total: {sum(a.V_balance for a in economy.agents.values()):.2f}")
print(f"  D total: {economy.rad.total_D():.2f}")
print(f"  θ: {economy.thermometer():.4f}")
print(f"  Population: {len(economy.agents)}")

print(f"\n📈 Analyse des composantes D:")
total_D = economy.rad.total_D()
if total_D > 0:
    print(f"  D_materielle:    {economy.rad.D_materielle:>10.2f} ({economy.rad.D_materielle/total_D*100:>5.1f}%)")
    print(f"  D_services:      {economy.rad.D_services:>10.2f} ({economy.rad.D_services/total_D*100:>5.1f}%)")
    print(f"  D_contractuelle: {economy.rad.D_contractuelle:>10.2f} ({economy.rad.D_contractuelle/total_D*100:>5.1f}%)")
    print(f"  D_engagement:    {economy.rad.D_engagement:>10.2f} ({economy.rad.D_engagement/total_D*100:>5.1f}%)")
    print(f"  D_regulatrice:   {economy.rad.D_regulatrice:>10.2f} ({economy.rad.D_regulatrice/total_D*100:>5.1f}%)")
    print(f"  TOTAL:           {total_D:>10.2f}")

print("\n" + "="*70)
