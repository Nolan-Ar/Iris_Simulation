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
from iris.utils.config_loader import load_config, get_config_value


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

    # Configuration
    parser.add_argument(
        '--config', type=str, default=None,
        help='Chemin vers le fichier de configuration YAML (défaut: config.yaml si existe)'
    )
    parser.add_argument(
        '--scenario', type=str, default=None,
        help='Nom du scénario prédéfini (baseline_stable, crisis_high_volatility, no_regulation, regulation_only)'
    )
    parser.add_argument(
        '--steps', type=int, default=None,
        help='Nombre de steps (mois) de simulation. Si non spécifié, utilise --years ou config'
    )

    # Paramètres de base
    parser.add_argument(
        '--population', type=int, default=None,
        help='Nombre d\'agents initiaux (défaut: depuis config ou 100)'
    )
    parser.add_argument(
        '--years', type=int, default=None,
        help='Durée de la simulation en années (défaut: depuis config ou 100)'
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


def load_and_merge_config(args):
    """
    Charge la configuration et fusionne avec les arguments CLI

    Priorité: CLI args > Scenario config > config.yaml > defaults
    """
    # Chargement du fichier de config
    config = None
    if args.config:
        config = load_config(args.config)
    else:
        # Tente de charger config.yaml par défaut
        default_config_path = Path(__file__).parent.parent.parent / "config.yaml"
        if default_config_path.exists():
            config = load_config(str(default_config_path))

    # Si un scénario est spécifié, charge ses paramètres
    scenario_config = None
    if args.scenario and config:
        scenario_config = get_config_value('scenarios', args.scenario, config=config)
        if not scenario_config:
            print(f"⚠ Scénario '{args.scenario}' non trouvé dans config.yaml")

    # Fusion des configs (scenario > config général)
    merged = {}

    # 1. Valeurs par défaut du code
    defaults = {
        'population': 100,
        'years': 100,
        'steps': None,
        'enable_demographics': True,
        'enable_catastrophes': False,
        'enable_price_discovery': True,
        'enable_business_combustion': True,
        'enable_dynamic_business': True,
        'enable_chambre_relance': True,
        'max_population': 10000,
        'mode_population': 'object',
        'transactions': 10,
    }
    merged.update(defaults)

    # 2. Config.yaml général
    if config:
        merged['population'] = get_config_value('simulation', 'population', 'default_size', default=defaults['population'], config=config)
        merged['steps'] = get_config_value('execution', 'default_steps', default=None, config=config)
        merged['enable_demographics'] = get_config_value('modules', 'enable_demographics', default=defaults['enable_demographics'], config=config)
        merged['enable_catastrophes'] = get_config_value('modules', 'enable_catastrophes', default=defaults['enable_catastrophes'], config=config)
        merged['enable_price_discovery'] = get_config_value('modules', 'enable_price_discovery', default=defaults['enable_price_discovery'], config=config)
        merged['enable_business_combustion'] = get_config_value('modules', 'enable_business_combustion', default=defaults['enable_business_combustion'], config=config)
        merged['enable_dynamic_business'] = get_config_value('modules', 'enable_dynamic_business', default=defaults['enable_dynamic_business'], config=config)
        merged['enable_chambre_relance'] = get_config_value('modules', 'enable_chambre_relance', default=defaults['enable_chambre_relance'], config=config)

    # 3. Scénario spécifique (override config général)
    if scenario_config:
        merged['population'] = scenario_config.get('population_size', merged['population'])
        merged['steps'] = scenario_config.get('steps', merged['steps'])

        # Modules du scénario
        if 'modules' in scenario_config:
            scenario_modules = scenario_config['modules']
            merged['enable_demographics'] = scenario_modules.get('enable_demographics', merged['enable_demographics'])
            merged['enable_catastrophes'] = scenario_modules.get('enable_catastrophes', merged['enable_catastrophes'])
            merged['enable_price_discovery'] = scenario_modules.get('enable_price_discovery', merged['enable_price_discovery'])
            merged['enable_business_combustion'] = scenario_modules.get('enable_business_combustion', merged['enable_business_combustion'])
            merged['enable_dynamic_business'] = scenario_modules.get('enable_dynamic_business', merged['enable_dynamic_business'])

    # 4. Arguments CLI (priorité maximale)
    if args.population is not None:
        merged['population'] = args.population
    if args.steps is not None:
        merged['steps'] = args.steps
    elif args.years is not None:
        # Conversion années → steps (1 step = 1 mois)
        merged['steps'] = args.years * 12

    # Modules CLI (--no-demographics, etc.)
    if args.no_demographics:
        merged['enable_demographics'] = False
    if args.no_catastrophes:
        merged['enable_catastrophes'] = False
    if args.no_prices:
        merged['enable_price_discovery'] = False
    if args.no_business:
        merged['enable_dynamic_business'] = False

    # Si steps toujours None, calculer depuis years ou config
    if merged['steps'] is None:
        if args.years is not None:
            merged['steps'] = args.years * 12
        else:
            merged['steps'] = merged.get('years', defaults['years']) * 12

    merged['mode_population'] = args.mode_population
    merged['max_population'] = args.max_population
    merged['transactions'] = args.transactions
    merged['seed'] = args.seed
    merged['taux_creation'] = args.taux_creation
    merged['taux_faillite'] = args.taux_faillite

    return merged


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

    # Charge et fusionne la configuration
    cfg = load_and_merge_config(args)

    print("\n" + "="*70)
    print("IRIS v2.1 - Système Économique Intégratif")
    print("="*70)

    # Affiche la config source
    if args.scenario:
        print(f"\n✓ Scénario: {args.scenario}")
    elif args.config:
        print(f"\n✓ Configuration: {args.config}")

    print(f"\nConfiguration de la simulation:")
    print(f"  Population initiale: {cfg['population']}")
    print(f"  Durée: {cfg['steps']} steps ({cfg['steps'] // 12} années)")
    print(f"  Mode population: {cfg['mode_population']}")
    print(f"  Démographie: {'Activée' if cfg['enable_demographics'] else 'Désactivée'}")
    print(f"  Catastrophes: {'Activées' if cfg['enable_catastrophes'] else 'Désactivées'}")
    print(f"  Prix explicites: {'Activés' if cfg['enable_price_discovery'] else 'Désactivés'}")
    print(f"  Entreprises dynamiques: {'Activées' if cfg['enable_dynamic_business'] else 'Désactivées'}")
    if cfg['seed'] is not None:
        print(f"  Graine aléatoire: {cfg['seed']}")
    print("="*70)

    # Création de l'économie IRIS
    economy = IRISEconomy(
        initial_agents=cfg['population'],
        enable_demographics=cfg['enable_demographics'],
        enable_catastrophes=cfg['enable_catastrophes'],
        enable_price_discovery=cfg['enable_price_discovery'],
        enable_dynamic_business=cfg['enable_dynamic_business'],
        enable_business_combustion=cfg['enable_business_combustion'],
        enable_chambre_relance=cfg['enable_chambre_relance'],
        # time_scale="years",  # DEPRECATED: toujours en mois maintenant (1 step = 1 mois)
        max_population=cfg['max_population'],
        initial_total_wealth_V=args.initial_total_V,
        mode_population=cfg['mode_population'],
        taux_creation_entreprises=cfg['taux_creation'],
        taux_faillite_entreprises=cfg['taux_faillite'],
        seed=cfg['seed']
    )

    # Exécution de la simulation
    # NOTE: 1 step = 1 mois (STEPS_PER_YEAR = 12)
    total_steps = cfg['steps']
    years = total_steps // 12
    print(f"\nDémarrage de la simulation ({years} années = {total_steps} mois/steps)...")

    try:
        for step in range(total_steps):
            economy.step(n_transactions=cfg['transactions'])

            # Affichage du progrès (tous les 12 steps = 1 an)
            if args.verbose or (step + 1) % 12 == 0:  # Affiche tous les ans
                theta = economy.thermometer()
                if economy.mode_population == "object":
                    pop = len(economy.agents)
                else:  # vectorized
                    pop = economy.population.total_population()
                current_year = (step + 1) // 12
                if (step + 1) % 12 == 0:  # Affiche seulement à la fin de chaque année
                    print(f"  Année {current_year}/{years} - Pop: {pop} - θ: {theta:.4f}")

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
