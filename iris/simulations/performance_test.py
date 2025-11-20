"""
IRIS Performance Test Script
=============================

Script de test de performance pour mesurer les performances de la simulation IRIS
avec différentes tailles de population.

Auteur: Arnault Nolan
Email: arnaultnolan@gmail.com
Date: 2025
"""

import sys
import time
from pathlib import Path
import json
from datetime import datetime
import traceback

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from iris.core.iris_model import IRISEconomy
import pandas as pd


def run_performance_test(population, years=100, seed=42):
    """
    Execute une simulation et mesure ses performances

    Args:
        population: Nombre d'agents initiaux
        years: Durée de la simulation en années
        seed: Graine aléatoire pour reproductibilité

    Returns:
        dict: Résultats de la simulation incluant métriques de performance
    """
    print(f"\n{'='*70}")
    print(f"Test de performance - Population: {population} agents")
    print(f"{'='*70}")

    # Initialisation
    start_time = time.time()

    try:
        # Création de l'économie
        init_start = time.time()
        economy = IRISEconomy(
            initial_agents=population,
            enable_demographics=True,
            enable_catastrophes=True,
            enable_price_discovery=True,
            enable_dynamic_business=True,
            # time_scale="years",  # DEPRECATED: toujours en mois (1 step = 1 mois)
            max_population=population * 20,  # Limite dynamique
            taux_creation_entreprises=0.05,
            taux_faillite_entreprises=0.03,
            seed=seed
        )
        init_time = time.time() - init_start

        # Exécution de la simulation
        # NOTE: years est en années, mais on simule en mois (1 step = 1 mois)
        total_steps = years * 12
        print(f"Simulation en cours ({years} années = {total_steps} mois/steps)...")
        sim_start = time.time()

        step_times = []
        for step in range(total_steps):
            step_start = time.time()
            economy.step(n_transactions=10)
            step_times.append(time.time() - step_start)

            # Affichage du progrès (tous les 12 steps = 1 an)
            if (step + 1) % 12 == 0:  # Affiche tous les ans
                current_year = (step + 1) // 12
                theta = economy.thermometer()
                pop = len(economy.agents)
                avg_step_time = sum(step_times[-12:]) / min(12, len(step_times))
                print(f"  Année {current_year}/{years} - Pop: {pop} - θ: {theta:.4f} - Temps/step moyen: {avg_step_time:.3f}s")

        sim_time = time.time() - sim_start
        total_time = time.time() - start_time

        # Collecte des statistiques
        final_stats = {
            # Configuration
            'population_initiale': population,
            'years': years,
            'seed': seed,

            # Performance
            'init_time': init_time,
            'simulation_time': sim_time,
            'total_time': total_time,
            'avg_step_time': sum(step_times) / len(step_times),
            'min_step_time': min(step_times),
            'max_step_time': max(step_times),

            # État final
            'population_finale': len(economy.agents),
            'total_V': sum(a.V_balance for a in economy.agents.values()),
            'total_U': sum(a.U_balance for a in economy.agents.values()),
            'total_D': economy.rad.total_D(),
            'thermometre': economy.thermometer(),
            'indicator': economy.indicator(),
            'gini': economy.gini_coefficient(),
            'kappa': economy.rad.kappa,
            'eta': economy.rad.eta,

            # Démographie
            'total_naissances': sum(economy.history['births']),
            'total_deces': sum(economy.history['deaths']),

            # Catastrophes
            'total_catastrophes': sum(economy.history['catastrophes']),

            # Prix
            'prix_moyen_final': economy.history['prix_moyen'][-1] if economy.history['prix_moyen'] else 0,
            'inflation_finale': economy.history['inflation'][-1] if economy.history['inflation'] else 0,

            # Entreprises
            'entreprises_actives': len(economy.entreprise_manager.entreprises_actives) if economy.enable_dynamic_business else len(economy.registre_entreprises.comptes),
            'total_creations_entreprises': sum(economy.history['creations_entreprises']) if economy.enable_dynamic_business else 0,
            'total_faillites_entreprises': sum(economy.history['faillites_entreprises']) if economy.enable_dynamic_business else 0,

            # Régulation RAD
            'C2_activations': sum(economy.history['C2_activated']),
            'C3_activations': sum(economy.history['C3_activated']),

            # Timestamp
            'timestamp': datetime.now().isoformat(),
        }

        # Affichage du résumé
        print(f"\n{'='*70}")
        print(f"RÉSULTATS - Population: {population}")
        print(f"{'='*70}")
        print(f"Temps d'initialisation: {init_time:.2f}s")
        print(f"Temps de simulation: {sim_time:.2f}s")
        print(f"Temps total: {total_time:.2f}s")
        print(f"Temps moyen/step: {final_stats['avg_step_time']:.4f}s")
        print(f"\nPopulation finale: {final_stats['population_finale']}")
        print(f"Thermomètre θ: {final_stats['thermometre']:.4f}")
        print(f"Indicateur I: {final_stats['indicator']:.4f}")
        print(f"Gini: {final_stats['gini']:.4f}")
        print(f"{'='*70}")

        return {
            'success': True,
            'stats': final_stats,
            'history': economy.history,
            'step_times': step_times
        }

    except Exception as e:
        print(f"\n✗ ERREUR pendant la simulation: {e}")
        traceback.print_exc()
        return {
            'success': False,
            'error': str(e),
            'population': population,
            'timestamp': datetime.now().isoformat()
        }


def main():
    """Fonction principale - Execute les tests de performance"""
    print("\n" + "="*70)
    print("IRIS v2.1 - TESTS DE PERFORMANCE")
    print("="*70)
    print("\nTests prévus: 100, 500, 1000 agents")
    print("Durée de chaque simulation: 100 années")
    print("Graine aléatoire fixe: 42 (reproductibilité)")
    print("="*70)

    # Configuration des tests
    test_populations = [100, 500, 1000]
    years = 100
    seed = 42

    # Stockage des résultats
    all_results = []

    # Exécution des tests
    start_global = time.time()

    for pop in test_populations:
        result = run_performance_test(pop, years, seed)
        all_results.append(result)

        # Pause entre les tests
        if pop != test_populations[-1]:
            print("\nPause de 2 secondes avant le prochain test...")
            time.sleep(2)

    total_global_time = time.time() - start_global

    # Sauvegarde des résultats
    print(f"\n{'='*70}")
    print("SAUVEGARDE DES RÉSULTATS")
    print(f"{'='*70}")

    output_dir = Path("performance_data")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Créer un timestamp pour les fichiers
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 1. Sauvegarder le résumé JSON
    summary_file = output_dir / f"performance_summary_{timestamp}.json"
    summary_data = {
        'test_date': datetime.now().isoformat(),
        'total_test_time': total_global_time,
        'test_populations': test_populations,
        'years_per_test': years,
        'seed': seed,
        'results': [r['stats'] if r['success'] else r for r in all_results]
    }

    with open(summary_file, 'w') as f:
        json.dump(summary_data, f, indent=2)
    print(f"✓ Résumé sauvegardé: {summary_file}")

    # 2. Sauvegarder les statistiques détaillées en CSV
    successful_results = [r for r in all_results if r['success']]
    if successful_results:
        stats_df = pd.DataFrame([r['stats'] for r in successful_results])
        stats_file = output_dir / f"performance_stats_{timestamp}.csv"
        stats_df.to_csv(stats_file, index=False)
        print(f"✓ Statistiques détaillées: {stats_file}")

    # 3. Sauvegarder les historiques complets
    for i, result in enumerate(successful_results):
        if result['success']:
            pop = result['stats']['population_initiale']
            history_df = pd.DataFrame(result['history'])
            history_file = output_dir / f"history_{pop}agents_{timestamp}.csv"
            history_df.to_csv(history_file, index=False)
            print(f"✓ Historique {pop} agents: {history_file}")

    # 4. Sauvegarder les temps par step
    for i, result in enumerate(successful_results):
        if result['success']:
            pop = result['stats']['population_initiale']
            step_times_df = pd.DataFrame({
                'year': range(len(result['step_times'])),
                'step_time': result['step_times']
            })
            step_times_file = output_dir / f"step_times_{pop}agents_{timestamp}.csv"
            step_times_df.to_csv(step_times_file, index=False)
            print(f"✓ Temps par step {pop} agents: {step_times_file}")

    # Affichage du résumé comparatif
    print(f"\n{'='*70}")
    print("RÉSUMÉ COMPARATIF")
    print(f"{'='*70}")
    print(f"Temps total des tests: {total_global_time:.2f}s ({total_global_time/60:.2f} minutes)")
    print()
    print(f"{'Population':<12} {'Init (s)':<10} {'Sim (s)':<10} {'Total (s)':<10} {'Step (ms)':<10}")
    print("-" * 70)

    for result in successful_results:
        if result['success']:
            stats = result['stats']
            pop = stats['population_initiale']
            init_t = stats['init_time']
            sim_t = stats['simulation_time']
            total_t = stats['total_time']
            avg_step = stats['avg_step_time'] * 1000  # ms
            print(f"{pop:<12} {init_t:<10.2f} {sim_t:<10.2f} {total_t:<10.2f} {avg_step:<10.2f}")

    print(f"{'='*70}")
    print("\n✓ Tests de performance terminés!")
    print(f"✓ Résultats disponibles dans le dossier: {output_dir}/")

    return 0


if __name__ == "__main__":
    sys.exit(main())
