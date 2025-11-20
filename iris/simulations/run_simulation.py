"""
IRIS Simulation - Script Universel
===================================

Script de simulation unique et modulaire pour le système IRIS v2.1

Fusionne et remplace tous les anciens scripts:
- run_simulation.py
- run_simulation_v2_1.py
- run_full_simulation.py
- run_longterm_simulation.py

Auteur: Arnault Nolan
Email: arnaultnolan@gmail.com
Date: 2025
"""

import argparse
import sys
from pathlib import Path
import numpy as np

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from iris.core.iris_model import IRISEconomy
from iris.analysis.iris_visualizer import IRISVisualizer


def parse_arguments():
    """Parse les arguments de la ligne de commande"""
    parser = argparse.ArgumentParser(
        description="Simulation IRIS v2.1 - Système économique modulaire",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:

  # Simulation de base (100 agents, 100 ans)
  python -m iris.simulations.run_simulation

  # Simulation longue durée avec forte population
  python -m iris.simulations.run_simulation --population 1000 --years 500

  # Simulation sans prix ni entreprises dynamiques
  python -m iris.simulations.run_simulation --no-prices --no-business

  # Simulation reproductible avec graine fixe
  python -m iris.simulations.run_simulation --seed 42

  # Simulation complète avec visualisations
  python -m iris.simulations.run_simulation --population 500 --years 200 --visualize
        """
    )

    # Paramètres de base
    parser.add_argument(
        '--population', type=int, default=100,
        help='Nombre d\'agents initiaux (défaut: 100)'
    )
    parser.add_argument(
        '--years', type=int, default=100,
        help='Durée de la simulation en années (défaut: 100)'
    )
    parser.add_argument(
        '--max-population', '--max-pop', type=int, default=10000,
        help='Population maximale (0 = illimité, défaut: 10000)'
    )
    parser.add_argument(
        '--initial-total-V', type=float, default=None,
        help='Richesse totale initiale en V à répartir entre les agents (défaut: auto ~5.78 V/agent)'
    )

    # Modules optionnels
    parser.add_argument(
        '--no-demographics', action='store_true',
        help='Désactive la démographie (naissances/décès)'
    )
    parser.add_argument(
        '--no-catastrophes', action='store_true',
        help='Désactive les catastrophes aléatoires'
    )
    parser.add_argument(
        '--no-prices', action='store_true',
        help='Désactive le mécanisme de prix explicites'
    )
    parser.add_argument(
        '--no-business', action='store_true',
        help='Désactive les entreprises dynamiques'
    )

    # Paramètres avancés
    parser.add_argument(
        '--mode-population', '--mode', type=str, default='object',
        choices=['object', 'vectorized'],
        help='Mode de gestion de la population: "object" (détaillé, lent) ou "vectorized" (rapide, grandes populations) (défaut: object)'
    )
    parser.add_argument(
        '--seed', type=int, default=None,
        help='Graine aléatoire pour reproductibilité (défaut: aléatoire)'
    )
    parser.add_argument(
        '--transactions', type=int, default=10,
        help='Nombre de transactions par pas de temps (défaut: 10)'
    )
    parser.add_argument(
        '--taux-creation', type=float, default=0.05,
        help='Taux de création d\'entreprises (défaut: 0.05)'
    )
    parser.add_argument(
        '--taux-faillite', type=float, default=0.03,
        help='Taux de faillite d\'entreprises (défaut: 0.03)'
    )

    # Sortie et visualisation
    parser.add_argument(
        '--visualize', action='store_true',
        help='Génère les visualisations après la simulation'
    )
    parser.add_argument(
        '--output-dir', type=str, default='data',
        help='Répertoire de sortie pour les résultats (défaut: data)'
    )
    parser.add_argument(
        '--verbose', action='store_true',
        help='Affiche plus d\'informations pendant la simulation'
    )

    return parser.parse_args()


def print_summary(economy: IRISEconomy):
    """Affiche un résumé de la simulation"""
    print("\n" + "="*70)
    print("RÉSUMÉ DE LA SIMULATION IRIS v2.1")
    print("="*70)

    print(f"\nDurée: {economy.time} années")

    # Mode de population
    if economy.mode_population == "object":
        print(f"Population finale: {len(economy.agents)} agents (mode: object)")
        total_V = sum(a.V_balance for a in economy.agents.values())
        total_U = sum(a.U_balance for a in economy.agents.values())
    else:  # vectorized
        print(f"Population finale: {economy.population.total_population()} agents (mode: vectorized)")
        total_V = economy.population.total_V()
        total_U = economy.population.total_U()

    # Statistiques économiques
    total_D = economy.rad.total_D()
    theta = economy.thermometer()
    indicator = economy.indicator()
    gini = economy.gini_coefficient()

    print(f"\nÉconomie:")
    print(f"  V total: {total_V:,.2f}")
    print(f"  U total: {total_U:,.2f}")
    print(f"  D total: {total_D:,.2f}")
    print(f"  Thermomètre θ: {theta:.4f}")
    print(f"  Indicateur I: {indicator:.4f}")
    print(f"  Gini: {gini:.4f}")
    print(f"  κ (kappa): {economy.rad.kappa:.4f}")
    print(f"  η (eta): {economy.rad.eta:.4f}")

    # Démographie
    if economy.enable_demographics and economy.demographics:
        if economy.mode_population == "object":
            stats_demo = economy.demographics.get_statistics(economy.agent_ages)
            print(f"\nDémographie:")
            print(f"  Âge moyen: {stats_demo['age_moyen']:.1f} ans")
        else:  # vectorized
            print(f"\nDémographie:")
            print(f"  Âge moyen: {economy.population.average_age():.1f} ans")
        print(f"  Naissances totales: {sum(economy.history['births'])}")
        print(f"  Décès totaux: {sum(economy.history['deaths'])}")

    # Catastrophes
    if economy.enable_catastrophes and economy.catastrophe_manager:
        total_catastrophes = sum(economy.history['catastrophes'])
        print(f"\nCatastrophes: {total_catastrophes} événements")

    # Prix et inflation
    if economy.enable_price_discovery and economy.price_manager:
        prix_moyen_final = economy.history['prix_moyen'][-1] if economy.history['prix_moyen'] else 0
        inflation_finale = economy.history['inflation'][-1] if economy.history['inflation'] else 0
        print(f"\nPrix:")
        print(f"  Prix moyen final: {prix_moyen_final:.2f}")
        print(f"  Inflation finale: {inflation_finale:.2%}")

    # Entreprises
    if economy.enable_dynamic_business and economy.entreprise_manager:
        nb_entreprises = len(economy.entreprise_manager.entreprises_actives)
        total_creations = sum(economy.history['creations_entreprises'])
        total_faillites = sum(economy.history['faillites_entreprises'])
        print(f"\nEntreprises:")
        print(f"  Actives: {nb_entreprises}")
        print(f"  Créations totales: {total_creations}")
        print(f"  Faillites totales: {total_faillites}")
    else:
        nb_entreprises_static = len(economy.registre_entreprises.comptes)
        print(f"\nEntreprises statiques: {nb_entreprises_static}")

    # Régulation RAD
    c2_activations = sum(economy.history['C2_activated'])
    c3_activations = sum(economy.history['C3_activated'])
    print(f"\nRégulation RAD:")
    print(f"  Activations C2: {c2_activations}")
    print(f"  Activations C3: {c3_activations}")

    print("\n" + "="*70)


def main():
    """Fonction principale"""
    args = parse_arguments()

    print("\n" + "="*70)
    print("IRIS v2.1 - Système Économique Intégratif")
    print("="*70)
    print(f"\nConfiguration de la simulation:")
    print(f"  Population initiale: {args.population}")
    print(f"  Durée: {args.years} années")
    print(f"  Mode population: {args.mode_population}")
    print(f"  Démographie: {'Désactivée' if args.no_demographics else 'Activée'}")
    print(f"  Catastrophes: {'Désactivées' if args.no_catastrophes else 'Activées'}")
    print(f"  Prix explicites: {'Désactivés' if args.no_prices else 'Activés'}")
    print(f"  Entreprises dynamiques: {'Désactivées' if args.no_business else 'Activées'}")
    if args.seed is not None:
        print(f"  Graine aléatoire: {args.seed}")
    print("="*70)

    # Création de l'économie IRIS
    economy = IRISEconomy(
        initial_agents=args.population,
        enable_demographics=not args.no_demographics,
        enable_catastrophes=not args.no_catastrophes,
        enable_price_discovery=not args.no_prices,
        enable_dynamic_business=not args.no_business,
        time_scale="years",
        max_population=args.max_population,
        initial_total_wealth_V=args.initial_total_V,
        mode_population=args.mode_population,
        taux_creation_entreprises=args.taux_creation,
        taux_faillite_entreprises=args.taux_faillite,
        seed=args.seed
    )

    # Exécution de la simulation
    print(f"\nDémarrage de la simulation ({args.years} années)...")

    try:
        for year in range(args.years):
            economy.step(n_transactions=args.transactions)

            # Affichage du progrès
            if args.verbose or (year + 1) % max(1, args.years // 20) == 0:
                theta = economy.thermometer()
                if economy.mode_population == "object":
                    pop = len(economy.agents)
                else:  # vectorized
                    pop = economy.population.total_population()
                print(f"  Année {year + 1}/{args.years} - Pop: {pop} - θ: {theta:.4f}")

        print("\n✓ Simulation terminée avec succès!")

        # Affichage du résumé
        print_summary(economy)

        # Génération des visualisations si demandé
        if args.visualize:
            print("\nGénération des visualisations...")
            output_path = Path(args.output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            visualizer = IRISVisualizer()
            visualizer.plot_full_history(
                economy.history,
                save_path=output_path / "iris_simulation.png"
            )

            print(f"✓ Visualisations sauvegardées dans {output_path}/")

        # Sauvegarde des données
        output_path = Path(args.output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        import pandas as pd
        df = pd.DataFrame(economy.history)
        csv_path = output_path / "history.csv"
        df.to_csv(csv_path, index=False)
        print(f"✓ Données sauvegardées dans {csv_path}")

    except KeyboardInterrupt:
        print("\n\n⚠ Simulation interrompue par l'utilisateur")
        return 1
    except Exception as e:
        print(f"\n\n✗ Erreur pendant la simulation: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
