#!/usr/bin/env python3
"""
Test des 3 scénarios thermodynamiques IRIS (ÉTAPE 3)

Ce script teste les corrections A-G appliquées au système RAD
en soumettant l'économie à 3 régimes thermodynamiques :
1. Sous-chauffe (θ < 1) : RAD doit stimuler
2. Normal (θ ≈ 1) : RAD doit maintenir
3. Surchauffe (θ > 1) : RAD doit freiner
"""

import sys
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent))

from iris.core.iris_scenarios import ScenarioRunner


def main():
    """Exécute les 3 scénarios thermodynamiques"""

    print("\n" + "="*70)
    print("TEST DES SCÉNARIOS THERMODYNAMIQUES - ÉTAPE 3")
    print("="*70)
    print("\nObjectif : Valider les corrections A-G du système RAD")
    print("Système tri-capteur : r_t, ν_eff, τ_eng")
    print("Bornes strictes : η, κ ∈ [0.7, 1.3]")
    print("Contraintes : |Δη|, |Δκ| ≤ 0.15")
    print("="*70)

    # Initialiser le runner de scénarios
    runner = ScenarioRunner(n_agents=100, output_dir="results/thermodynamic")

    # === SCÉNARIO 1 : SOUS-CHAUFFE ===
    print("\n\n" + "="*70)
    print("TEST 1/3 : SOUS-CHAUFFE")
    print("="*70)

    try:
        economy_underheat = runner.run_thermodynamic_underheat(steps=600)
        print("\n✓ Scénario SOUS-CHAUFFE terminé")
    except Exception as e:
        print(f"\n✗ Erreur scénario SOUS-CHAUFFE : {e}")
        import traceback
        traceback.print_exc()
        return 1

    # === SCÉNARIO 2 : NORMAL ===
    print("\n\n" + "="*70)
    print("TEST 2/3 : NORMAL (ÉQUILIBRE)")
    print("="*70)

    try:
        economy_normal = runner.run_thermodynamic_normal(steps=600)
        print("\n✓ Scénario NORMAL terminé")
    except Exception as e:
        print(f"\n✗ Erreur scénario NORMAL : {e}")
        import traceback
        traceback.print_exc()
        return 1

    # === SCÉNARIO 3 : SURCHAUFFE ===
    print("\n\n" + "="*70)
    print("TEST 3/3 : SURCHAUFFE")
    print("="*70)

    try:
        economy_overheat = runner.run_thermodynamic_overheat(steps=600)
        print("\n✓ Scénario SURCHAUFFE terminé")
    except Exception as e:
        print(f"\n✗ Erreur scénario SURCHAUFFE : {e}")
        import traceback
        traceback.print_exc()
        return 1

    # === RÉSUMÉ COMPARATIF ===
    print("\n\n" + "="*70)
    print("RÉSUMÉ COMPARATIF DES 3 SCÉNARIOS")
    print("="*70)

    print(f"\n{'Scénario':<20} {'θ final':<12} {'κ final':<12} {'η final':<12}")
    print("-" * 70)

    theta_underheat = economy_underheat.thermometer()
    kappa_underheat = economy_underheat.rad.kappa
    eta_underheat = economy_underheat.rad.eta
    print(f"{'Sous-chauffe':<20} {theta_underheat:<12.4f} {kappa_underheat:<12.4f} {eta_underheat:<12.4f}")

    theta_normal = economy_normal.thermometer()
    kappa_normal = economy_normal.rad.kappa
    eta_normal = economy_normal.rad.eta
    print(f"{'Normal':<20} {theta_normal:<12.4f} {kappa_normal:<12.4f} {eta_normal:<12.4f}")

    theta_overheat = economy_overheat.thermometer()
    kappa_overheat = economy_overheat.rad.kappa
    eta_overheat = economy_overheat.rad.eta
    print(f"{'Surchauffe':<20} {theta_overheat:<12.4f} {kappa_overheat:<12.4f} {eta_overheat:<12.4f}")

    print("\n" + "="*70)
    print("VALIDATION GLOBALE")
    print("="*70)

    # Compteur de tests réussis
    success_count = 0
    total_tests = 3

    # Test 1 : Sous-chauffe - θ doit revenir vers 1
    if 0.8 <= theta_underheat <= 1.2:
        print("✓ Sous-chauffe : θ stabilisé autour de 1.0")
        success_count += 1
    else:
        print(f"✗ Sous-chauffe : θ = {theta_underheat:.4f} (hors cible)")

    # Test 2 : Normal - θ doit rester proche de 1
    if 0.8 <= theta_normal <= 1.2:
        print("✓ Normal : équilibre maintenu")
        success_count += 1
    else:
        print(f"✗ Normal : θ = {theta_normal:.4f} (dérive)")

    # Test 3 : Surchauffe - θ doit revenir vers 1
    if 0.8 <= theta_overheat <= 1.2:
        print("✓ Surchauffe : θ stabilisé autour de 1.0")
        success_count += 1
    else:
        print(f"✗ Surchauffe : θ = {theta_overheat:.4f} (hors cible)")

    print("\n" + "="*70)
    print(f"RÉSULTAT FINAL : {success_count}/{total_tests} tests réussis")
    print("="*70)

    if success_count == total_tests:
        print("\n🎉 SUCCÈS : Le système RAD fonctionne correctement !")
        print("   Les corrections A-G sont validées.")
        return 0
    else:
        print(f"\n⚠ PARTIEL : {success_count}/{total_tests} scénarios validés")
        print("   Ajustements nécessaires pour stabilisation complète.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
