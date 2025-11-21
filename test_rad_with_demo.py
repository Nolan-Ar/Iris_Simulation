#!/usr/bin/env python3
"""Test RAD avec démographie et consumption_D_per_year corrigé"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from iris.core.iris_model import IRISEconomy


def test_rad_with_demographics():
    """Test RAD avec démographie (consumption_D_per_year = 0.5)"""
    print("\n" + "="*70)
    print("TEST RAD - AVEC DÉMOGRAPHIE (consumption_D_per_year = 0.5)")
    print("="*70)

    economy = IRISEconomy(
        initial_agents=100,
        enable_demographics=True,   # ACTIVÉ
        enable_catastrophes=False,
        enable_business_combustion=True,
        enable_dynamic_business=True,   # ACTIVÉ pour combustion
        enable_chambre_relance=False,
        seed=42
    )

    print(f"\nÉtat initial:")
    print(f"  θ: {economy.thermometer():.4f}")
    print(f"  κ: {economy.rad.kappa:.4f}")
    print(f"  η: {economy.rad.eta:.4f}")
    print(f"  consumption_D_per_year: {economy.demographics.consumption_D_per_year}")

    print(f"\nSimulation 600 steps (50 ans) avec démographie...")

    for i in range(600):
        economy.step(n_transactions=10)

        if (i + 1) % 120 == 0:
            years = (i + 1) // 12
            theta = economy.thermometer()
            kappa = economy.rad.kappa
            eta = economy.rad.eta
            V_total = sum(a.V_balance for a in economy.agents.values())
            D_total = economy.rad.total_D()
            pop = len(economy.agents)
            print(f"  +{years} ans: θ={theta:.4f}, κ={kappa:.4f}, η={eta:.4f}, V={V_total:.0f}, D={D_total:.0f}, Pop={pop}")

    print(f"\nRÉSULTATS FINAUX:")
    theta_final = economy.thermometer()
    kappa_final = economy.rad.kappa
    eta_final = economy.rad.eta

    print(f"  θ final: {theta_final:.4f} (cible: 1.0)")
    print(f"  κ final: {kappa_final:.4f}")
    print(f"  η final: {eta_final:.4f}")
    print(f"  Population finale: {len(economy.agents)}")

    # Analyse D components
    D_mat = economy.rad.D_materielle
    D_ser = economy.rad.D_services
    D_con = economy.rad.D_contractuelle
    D_eng = economy.rad.D_engagement
    D_reg = economy.rad.D_regulatrice
    D_tot = economy.rad.total_D()

    print(f"\n  Composantes de D:")
    print(f"    D_materielle:    {D_mat:>10.2f} ({D_mat/D_tot*100:>5.1f}%)")
    print(f"    D_services:      {D_ser:>10.2f} ({D_ser/D_tot*100:>5.1f}%)")
    print(f"    D_contractuelle: {D_con:>10.2f} ({D_con/D_tot*100:>5.1f}%)")
    print(f"    D_engagement:    {D_eng:>10.2f} ({D_eng/D_tot*100:>5.1f}%)")
    print(f"    D_regulatrice:   {D_reg:>10.2f} ({D_reg/D_tot*100:>5.1f}%)")
    print(f"    TOTAL:           {D_tot:>10.2f}")

    if 0.9 <= theta_final <= 1.1:
        print(f"\n✓ SUCCÈS: θ stabilisé autour de 1.0")
        return 0
    else:
        print(f"\n✗ ÉCHEC: θ = {theta_final:.4f}")
        return 1


if __name__ == "__main__":
    sys.exit(test_rad_with_demographics())
