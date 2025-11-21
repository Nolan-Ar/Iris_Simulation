#!/usr/bin/env python3
"""
Test RAD PUR sans démographie (ÉTAPE 3 - DEBUG)

Test du système tri-capteur sans le bruit de la démographie
pour isoler le comportement du RAD.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from iris.core.iris_model import IRISEconomy


def test_rad_normal():
    """Test RAD sans chocs ni démographie"""
    print("\n" + "="*70)
    print("TEST RAD PUR - SCÉNARIO NORMAL (sans démographie)")
    print("="*70)

    economy = IRISEconomy(
        initial_agents=100,
        enable_demographics=False,  # DÉSACTIVÉ
        enable_catastrophes=False,
        enable_business_combustion=True,
        enable_dynamic_business=False,  # DÉSACTIVÉ
        enable_chambre_relance=False,  # DÉSACTIVÉ
        seed=42
    )

    print(f"\nÉtat initial:")
    print(f"  θ: {economy.thermometer():.4f}")
    print(f"  κ: {economy.rad.kappa:.4f}")
    print(f"  η: {economy.rad.eta:.4f}")
    print(f"  V_total: {sum(a.V_balance for a in economy.agents.values()):.2f}")
    print(f"  D_total: {economy.rad.total_D():.2f}")

    print(f"\nSimulation 600 steps (50 ans)...")

    for i in range(600):
        economy.step(n_transactions=10)

        if (i + 1) % 120 == 0:
            years = (i + 1) // 12
            theta = economy.thermometer()
            kappa = economy.rad.kappa
            eta = economy.rad.eta
            V_total = sum(a.V_balance for a in economy.agents.values())
            D_total = economy.rad.total_D()
            print(f"  +{years} ans: θ={theta:.4f}, κ={kappa:.4f}, η={eta:.4f}, V={V_total:.0f}, D={D_total:.0f}")

    print(f"\nRÉSULTATS FINAUX:")
    theta_final = economy.thermometer()
    kappa_final = economy.rad.kappa
    eta_final = economy.rad.eta

    print(f"  θ final: {theta_final:.4f} (cible: 1.0)")
    print(f"  κ final: {kappa_final:.4f}")
    print(f"  η final: {eta_final:.4f}")

    if 0.9 <= theta_final <= 1.1:
        print(f"\n✓ SUCCÈS: θ stabilisé autour de 1.0")
        return 0
    else:
        print(f"\n✗ ÉCHEC: θ = {theta_final:.4f}")
        return 1


if __name__ == "__main__":
    sys.exit(test_rad_normal())
