"""
Test rapide de experiment_grid avec grille réduite
===================================================

Lance quelques expériences pour valider le système.
"""

from pathlib import Path
import sys
import pandas as pd

# Import du module experiment_grid
from iris.simulations.experiment_grid import (
    ExperimentConfig,
    run_single_experiment,
    print_summary_statistics
)


def run_small_test():
    """Lance quelques expériences de test."""

    print("\n" + "="*80)
    print("TEST RAPIDE - GRILLE RÉDUITE")
    print("="*80 + "\n")

    # Grille réduite pour test rapide
    test_configs = [
        # Petit système, court
        ExperimentConfig(
            initial_agents=100,
            enable_catastrophes=False,
            conservation_rate=0.05,
            seed=1,
            steps=120  # 10 ans
        ),

        # Avec catastrophes
        ExperimentConfig(
            initial_agents=100,
            enable_catastrophes=True,
            conservation_rate=0.05,
            seed=1,
            steps=120
        ),

        # Sans conservation RU
        ExperimentConfig(
            initial_agents=100,
            enable_catastrophes=False,
            conservation_rate=0.0,
            seed=1,
            steps=120
        ),

        # Plus grande population
        ExperimentConfig(
            initial_agents=200,
            enable_catastrophes=False,
            conservation_rate=0.05,
            seed=1,
            steps=120
        ),
    ]

    output_dir = Path("results/test_grid")
    summaries = []

    for i, config in enumerate(test_configs):
        print(f"\n[{i+1}/{len(test_configs)}]")
        summary = run_single_experiment(config, output_dir)
        summaries.append(summary)

    # Création du résumé
    df_summary = pd.DataFrame(summaries)
    summary_path = output_dir / "summary.csv"
    df_summary.to_csv(summary_path, index=False)

    print(f"\n{'='*80}")
    print(f"TEST TERMINÉ")
    print(f"{'='*80}")
    print(f"Résultats: {output_dir.absolute()}")
    print(f"Résumé: {summary_path}")
    print(f"{'='*80}\n")

    # Affichage statistiques
    print_summary_statistics(df_summary)

    # Affichage du résumé
    print("\nRÉSUMÉ DES SCÉNARIOS:")
    print(df_summary[['scenario_name', 'theta_mean', 'theta_std', 'gini_final',
                      'population_final', 'catastrophes_total']].to_string(index=False))

    # Génération des graphiques d'analyse
    print("\n" + "="*80)
    print("📊 GÉNÉRATION DES GRAPHIQUES D'ANALYSE")
    print("="*80)
    try:
        from iris.simulations.plot_analysis import IRISPlotAnalysis
        analyzer = IRISPlotAnalysis(output_dir)
        analyzer.plot_all()
        print(f"\n✅ Graphiques disponibles dans: {output_dir / 'plots'}")
    except Exception as e:
        print(f"⚠ Erreur lors de la génération des graphiques: {e}")

    return df_summary


if __name__ == "__main__":
    df = run_small_test()
    print("\n✅ Test terminé avec succès!")
