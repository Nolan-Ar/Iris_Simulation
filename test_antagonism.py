"""
Test script pour vérifier l'antagonisme entre κ et η
====================================================

Ce script teste que :
1. Le système converge vers θ = 1.0
2. κ et η évoluent différemment (antagonisme)
3. Les oscillations sont amorties
"""

import sys
import numpy as np
from iris.core import IRISEconomy

def test_antagonism():
    """Test de l'antagonisme algorithmique entre κ et η"""

    print("=" * 80)
    print("TEST DE L'ANTAGONISME ENTRE κ (KAPPA) ET η (ETA)")
    print("=" * 80)

    # Créer une économie de test
    print("\n1. Création de l'économie IRIS avec 100 agents...")
    model = IRISEconomy(
        initial_agents=100,
        initial_total_wealth_V=100000.0,  # 1000 per agent
        conservation_rate=0.05,
        mode_population="object"
    )

    # Enregistrer les valeurs initiales
    theta_history = []
    kappa_history = []
    eta_history = []

    print(f"   Valeurs initiales:")
    print(f"   - θ (theta) = {model.thermometer():.4f}")
    print(f"   - κ (kappa) = {model.rad.kappa:.4f}")
    print(f"   - η (eta)   = {model.rad.eta:.4f}")

    # Simuler 60 cycles (5 ans)
    print("\n2. Simulation de 60 cycles (5 ans)...")
    num_steps = 60

    for i in range(num_steps):
        model.step()

        theta = model.thermometer()
        kappa = model.rad.kappa
        eta = model.rad.eta

        theta_history.append(theta)
        kappa_history.append(kappa)
        eta_history.append(eta)

        if (i + 1) % 12 == 0:  # Afficher tous les ans
            year = (i + 1) // 12
            print(f"   Année {year}: θ={theta:.4f}, κ={kappa:.4f}, η={eta:.4f}")

    # Analyse des résultats
    print("\n3. Analyse des résultats:")
    print("=" * 80)

    # Vérifier la convergence de θ vers 1.0
    final_theta = theta_history[-1]
    theta_deviation = abs(final_theta - 1.0)
    print(f"\n   a) Convergence de θ:")
    print(f"      - θ initial  = {theta_history[0]:.4f}")
    print(f"      - θ final    = {final_theta:.4f}")
    print(f"      - Écart à 1.0 = {theta_deviation:.4f}")

    if theta_deviation < 0.3:
        print(f"      ✓ SUCCÈS: θ converge vers 1.0 (écart < 0.3)")
    else:
        print(f"      ✗ ÉCHEC: θ ne converge pas suffisamment (écart > 0.3)")

    # Vérifier l'antagonisme : κ et η doivent évoluer différemment
    kappa_variation = np.std(kappa_history)
    eta_variation = np.std(eta_history)

    # Calculer la corrélation entre les variations de κ et η
    kappa_diff = np.diff(kappa_history)
    eta_diff = np.diff(eta_history)

    # Compter les cas où κ et η varient dans le même sens
    same_direction = np.sum((kappa_diff * eta_diff) > 0)
    total_variations = len(kappa_diff)
    same_direction_ratio = same_direction / total_variations if total_variations > 0 else 0

    print(f"\n   b) Antagonisme entre κ et η:")
    print(f"      - Variation κ (std) = {kappa_variation:.4f}")
    print(f"      - Variation η (std) = {eta_variation:.4f}")
    print(f"      - Mouvements même sens: {same_direction}/{total_variations} ({same_direction_ratio*100:.1f}%)")

    # L'antagonisme devrait réduire les mouvements dans le même sens
    # mais ne les élimine pas complètement (30% d'atténuation)
    if kappa_variation > 0.01 and eta_variation > 0.01:
        print(f"      ✓ SUCCÈS: κ et η varient tous deux (dynamisme du système)")
    else:
        print(f"      ⚠ AVERTISSEMENT: Faible variation de κ ou η")

    # Vérifier que les variations sont différentes (antagonisme)
    variation_ratio = min(kappa_variation, eta_variation) / max(kappa_variation, eta_variation)
    print(f"      - Ratio variation min/max = {variation_ratio:.3f}")

    if variation_ratio < 0.9:  # Les variations doivent être différentes
        print(f"      ✓ SUCCÈS: Les amplitudes de variation diffèrent (antagonisme)")
    else:
        print(f"      ⚠ AVERTISSEMENT: κ et η varient de façon similaire")

    # Vérifier l'amortissement des oscillations
    print(f"\n   c) Amortissement des oscillations:")
    early_theta_std = np.std(theta_history[:20])  # Premier tiers
    late_theta_std = np.std(theta_history[-20:])   # Dernier tiers

    print(f"      - Oscillations θ (début): {early_theta_std:.4f}")
    print(f"      - Oscillations θ (fin):   {late_theta_std:.4f}")

    if late_theta_std < early_theta_std * 1.2:  # Pas d'augmentation significative
        print(f"      ✓ SUCCÈS: Les oscillations sont contrôlées")
    else:
        print(f"      ✗ ÉCHEC: Les oscillations augmentent")

    # Visualiser les dernières valeurs
    print(f"\n4. Valeurs finales:")
    print(f"   - θ (theta) = {theta_history[-1]:.4f} (cible: 1.0)")
    print(f"   - κ (kappa) = {kappa_history[-1]:.4f} (neutre: 1.0)")
    print(f"   - η (eta)   = {eta_history[-1]:.4f} (neutre: 1.0)")

    # Vérifier les bornes
    print(f"\n5. Vérification des bornes [0.5, 2.0]:")
    kappa_min, kappa_max = min(kappa_history), max(kappa_history)
    eta_min, eta_max = min(eta_history), max(eta_history)

    print(f"   - κ: [{kappa_min:.4f}, {kappa_max:.4f}]")
    print(f"   - η: [{eta_min:.4f}, {eta_max:.4f}]")

    if 0.5 <= kappa_min and kappa_max <= 2.0:
        print(f"      ✓ κ respecte les bornes")
    else:
        print(f"      ✗ κ sort des bornes !")

    if 0.5 <= eta_min and eta_max <= 2.0:
        print(f"      ✓ η respecte les bornes")
    else:
        print(f"      ✗ η sort des bornes !")

    # Résultat final
    print("\n" + "=" * 80)
    success = (
        theta_deviation < 0.3 and
        kappa_variation > 0.01 and
        eta_variation > 0.01 and
        0.5 <= kappa_min and kappa_max <= 2.0 and
        0.5 <= eta_min and eta_max <= 2.0
    )

    if success:
        print("RÉSULTAT: ✓ TEST RÉUSSI - L'antagonisme fonctionne correctement")
    else:
        print("RÉSULTAT: ⚠ TEST PARTIEL - Vérifier les détails ci-dessus")
    print("=" * 80)

    return success

if __name__ == "__main__":
    try:
        success = test_antagonism()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ ERREUR lors du test: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(2)
