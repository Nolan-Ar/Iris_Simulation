"""
IRIS Experiment Grid
====================

Programme d'expériences systématiques avec grille de paramètres.

Ce script permet de tester l'effet de différents paramètres sur la stabilité
du système IRIS (θ, Gini, population, catastrophes).

Usage:
    python -m iris.simulations.experiment_grid

Résultats:
    results/grid/<scenario_name>/history.csv  (pour chaque scénario)
    results/grid/summary.csv                   (résumé global)
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
import itertools
import time
from datetime import datetime

import numpy as np
import pandas as pd

# Import IRIS
from iris.core import IRISEconomy

# Import visualizer si disponible
try:
    from iris.analysis.iris_visualizer import IRISVisualizer
    VISUALIZER_AVAILABLE = True
except ImportError:
    VISUALIZER_AVAILABLE = False
    print("⚠ IRISVisualizer non disponible - visualisations désactivées")


@dataclass
class ExperimentConfig:
    """Configuration d'une expérience unique."""
    initial_agents: int
    enable_catastrophes: bool
    conservation_rate: float
    seed: int
    steps: int

    def to_scenario_name(self) -> str:
        """Génère un nom de scénario lisible."""
        cata = 1 if self.enable_catastrophes else 0
        rho_str = f"{int(self.conservation_rate * 100):03d}"  # 000, 005, 015
        return f"N{self.initial_agents}_cata{cata}_rho{rho_str}_seed{self.seed}_t{self.steps}"

    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire."""
        return {
            'initial_agents': self.initial_agents,
            'enable_catastrophes': self.enable_catastrophes,
            'conservation_rate': self.conservation_rate,
            'seed': self.seed,
            'steps': self.steps,
            'scenario_name': self.to_scenario_name()
        }


def generate_parameter_grid() -> List[ExperimentConfig]:
    """
    Génère la grille complète de paramètres à tester.

    Returns:
        Liste de configurations d'expériences
    """
    # Définition de la grille
    param_grid = {
        'initial_agents': [200, 500, 1000],
        'enable_catastrophes': [True, False],
        'conservation_rate': [0.0, 0.05, 0.15],
        'seed': [1, 2, 3],
        'steps': [600, 1200]  # 50 ans ou 100 ans
    }

    # Génération de toutes les combinaisons
    keys = param_grid.keys()
    values = param_grid.values()
    combinations = list(itertools.product(*values))

    # Conversion en ExperimentConfig
    configs = []
    for combo in combinations:
        config_dict = dict(zip(keys, combo))
        configs.append(ExperimentConfig(**config_dict))

    return configs


def run_single_experiment(config: ExperimentConfig, output_dir: Path) -> Dict[str, Any]:
    """
    Lance une expérience unique avec une configuration donnée.

    Args:
        config: Configuration de l'expérience
        output_dir: Répertoire de sortie pour les résultats

    Returns:
        Dictionnaire avec résumé des résultats
    """
    scenario_name = config.to_scenario_name()
    scenario_dir = output_dir / scenario_name
    scenario_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*80}")
    print(f"Scénario: {scenario_name}")
    print(f"{'='*80}")
    print(f"  Agents: {config.initial_agents}")
    print(f"  Catastrophes: {config.enable_catastrophes}")
    print(f"  ρ (conservation): {config.conservation_rate}")
    print(f"  Seed: {config.seed}")
    print(f"  Steps: {config.steps}")

    # Création du modèle
    start_time = time.time()

    try:
        model = IRISEconomy(
            initial_agents=config.initial_agents,
            initial_total_wealth_V=config.initial_agents * 1000.0,  # 1000 V par agent
            conservation_rate=config.conservation_rate,
            enable_catastrophes=config.enable_catastrophes,
            enable_demographics=True,
            enable_chambre_relance=True,
            mode_population="object",
            seed=config.seed
        )

        # Initialisation de l'historique
        history: Dict[str, List] = {
            'time': [],
            'thermometer': [],
            'indicator': [],
            'kappa': [],
            'eta': [],
            'population': [],
            'total_V': [],
            'total_U': [],
            'total_D': [],
            'V_on': [],
            'gini_coefficient': [],
            'catastrophes': [],
            'births': [],
            'deaths': [],
            'C2_activated': [],
            'C3_activated': []
        }

        # Simulation
        print(f"  Simulation en cours...")
        n_transactions = 20  # Nombre de transactions par cycle

        for t in range(config.steps):
            # Avancer d'un cycle
            model.step()

            # Enregistrement des données
            theta = model.thermometer()
            indicator = model.indicator()
            V_on = model.get_V_on()
            total_V = sum(a.V_balance for a in model.agents.values())
            total_U = sum(a.U_balance for a in model.agents.values())
            total_D = model.rad.total_D()
            population = len(model.agents)

            # Calcul Gini (inégalité de richesse)
            gini = calculate_gini_coefficient(model)

            # Récupération stats du cycle
            catastrophes_this_cycle = getattr(model, '_catastrophes_this_step', 0)
            births_this_cycle = getattr(model, '_births_this_step', 0)
            deaths_this_cycle = getattr(model, '_deaths_this_step', 0)
            C2_activated = getattr(model, '_C2_activated', False)
            C3_activated = getattr(model, '_C3_activated', False)

            # Enregistrement
            history['time'].append(t)
            history['thermometer'].append(theta)
            history['indicator'].append(indicator)
            history['kappa'].append(model.rad.kappa)
            history['eta'].append(model.rad.eta)
            history['population'].append(population)
            history['total_V'].append(total_V)
            history['total_U'].append(total_U)
            history['total_D'].append(total_D)
            history['V_on'].append(V_on)
            history['gini_coefficient'].append(gini)
            history['catastrophes'].append(catastrophes_this_cycle)
            history['births'].append(births_this_cycle)
            history['deaths'].append(deaths_this_cycle)
            history['C2_activated'].append(C2_activated)
            history['C3_activated'].append(C3_activated)

            # Affichage progression (tous les 12 mois)
            if (t + 1) % 12 == 0:
                year = (t + 1) // 12
                print(f"    Année {year:3d}: θ={theta:.4f}, Pop={population:4d}, "
                      f"Gini={gini:.3f}, κ={model.rad.kappa:.3f}, η={model.rad.eta:.3f}")

        elapsed_time = time.time() - start_time
        print(f"  ✓ Simulation terminée en {elapsed_time:.1f}s")

        # Sauvegarde de l'historique complet
        df_history = pd.DataFrame(history)
        history_path = scenario_dir / "history.csv"
        df_history.to_csv(history_path, index=False)
        print(f"  ✓ Historique sauvegardé: {history_path}")

        # Calcul des résumés numériques
        theta_values = np.array(history['thermometer'])
        gini_values = np.array(history['gini_coefficient'])
        catastrophes_values = np.array(history['catastrophes'])

        summary = {
            # Métadonnées
            'scenario_name': scenario_name,
            'initial_agents': config.initial_agents,
            'enable_catastrophes': config.enable_catastrophes,
            'conservation_rate': config.conservation_rate,
            'seed': config.seed,
            'steps': config.steps,

            # Thermomètre
            'theta_mean': float(np.mean(theta_values)),
            'theta_std': float(np.std(theta_values)),
            'theta_final': float(theta_values[-1]),
            'theta_min': float(np.min(theta_values)),
            'theta_max': float(np.max(theta_values)),

            # Gini
            'gini_mean': float(np.mean(gini_values)),
            'gini_std': float(np.std(gini_values)),
            'gini_final': float(gini_values[-1]),

            # Catastrophes
            'catastrophes_total': int(np.sum(catastrophes_values)),
            'catastrophes_mean': float(np.mean(catastrophes_values)),

            # Population
            'population_initial': history['population'][0],
            'population_final': history['population'][-1],
            'population_mean': float(np.mean(history['population'])),

            # Régulation
            'kappa_mean': float(np.mean(history['kappa'])),
            'eta_mean': float(np.mean(history['eta'])),
            'C2_activations': int(np.sum(history['C2_activated'])),
            'C3_activations': int(np.sum(history['C3_activated'])),

            # Performance
            'elapsed_time_s': elapsed_time
        }

        # Visualisations (si disponible)
        if VISUALIZER_AVAILABLE:
            try:
                viz = IRISVisualizer(output_dir=str(scenario_dir))
                viz.plot_main_variables(history)
                viz.export_data(history, filename=f"data_{scenario_name}")
                print(f"  ✓ Visualisations créées")
            except Exception as e:
                print(f"  ⚠ Erreur visualisation: {e}")

        print(f"  ✓ Résumé: θ_mean={summary['theta_mean']:.4f}, "
              f"Gini={summary['gini_final']:.3f}, Pop={summary['population_final']}")

        return summary

    except Exception as e:
        print(f"  ✗ ERREUR: {e}")
        import traceback
        traceback.print_exc()

        # Retourne un résumé avec erreur
        return {
            'scenario_name': scenario_name,
            'initial_agents': config.initial_agents,
            'enable_catastrophes': config.enable_catastrophes,
            'conservation_rate': config.conservation_rate,
            'seed': config.seed,
            'steps': config.steps,
            'error': str(e)
        }


def calculate_gini_coefficient(model: IRISEconomy) -> float:
    """
    Calcule le coefficient de Gini pour mesurer l'inégalité de richesse.

    Args:
        model: Instance IRISEconomy

    Returns:
        Coefficient de Gini (0 = égalité parfaite, 1 = inégalité totale)
    """
    if len(model.agents) == 0:
        return 0.0

    # Richesse de chaque agent (V + U)
    wealth = np.array([agent.V_balance + agent.U_balance for agent in model.agents.values()])

    # Si tout le monde a 0, Gini = 0
    if np.sum(wealth) == 0:
        return 0.0

    # Tri croissant
    sorted_wealth = np.sort(wealth)
    n = len(sorted_wealth)

    # Formule du Gini
    cumsum = np.cumsum(sorted_wealth)
    gini = (2.0 * np.sum((np.arange(1, n + 1)) * sorted_wealth)) / (n * np.sum(sorted_wealth)) - (n + 1) / n

    return float(gini)


def run_all_grid(output_dir: Path = Path("results/grid")) -> pd.DataFrame:
    """
    Lance toutes les expériences de la grille de paramètres.

    Args:
        output_dir: Répertoire racine pour les résultats

    Returns:
        DataFrame avec résumé de tous les scénarios
    """
    # Création du répertoire de sortie
    output_dir.mkdir(parents=True, exist_ok=True)

    # Génération de la grille
    configs = generate_parameter_grid()
    total_experiments = len(configs)

    print(f"\n{'#'*80}")
    print(f"# IRIS EXPERIMENT GRID")
    print(f"{'#'*80}")
    print(f"Total d'expériences: {total_experiments}")
    print(f"Répertoire de sortie: {output_dir}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'#'*80}\n")

    # Lancement de toutes les expériences
    summaries = []
    start_time_global = time.time()

    for i, config in enumerate(configs):
        print(f"\n[{i+1}/{total_experiments}] ", end="")
        summary = run_single_experiment(config, output_dir)
        summaries.append(summary)

    elapsed_global = time.time() - start_time_global

    # Création du DataFrame de résumé
    df_summary = pd.DataFrame(summaries)

    # Sauvegarde du résumé global
    summary_path = output_dir / "summary.csv"
    df_summary.to_csv(summary_path, index=False)

    print(f"\n{'='*80}")
    print(f"EXPÉRIENCES TERMINÉES")
    print(f"{'='*80}")
    print(f"Total: {total_experiments} expériences")
    print(f"Temps total: {elapsed_global:.1f}s ({elapsed_global/60:.1f} min)")
    print(f"Résumé global: {summary_path}")
    print(f"{'='*80}\n")

    # Génération automatique des graphiques d'analyse
    print("📊 Génération des graphiques d'analyse...")
    try:
        from iris.simulations.plot_analysis import IRISPlotAnalysis
        analyzer = IRISPlotAnalysis(output_dir)
        analyzer.plot_all()
    except Exception as e:
        print(f"⚠ Erreur lors de la génération des graphiques: {e}")
        print("   (Les résultats CSV sont disponibles)")

    return df_summary


def print_summary_statistics(df_summary: pd.DataFrame) -> None:
    """
    Affiche des statistiques résumées sur les résultats.

    Args:
        df_summary: DataFrame avec les résumés
    """
    print("\n" + "="*80)
    print("STATISTIQUES GLOBALES")
    print("="*80)

    # Statistiques θ
    print("\n📊 Thermomètre θ:")
    print(f"  θ moyen global: {df_summary['theta_mean'].mean():.4f} ± {df_summary['theta_mean'].std():.4f}")
    print(f"  θ std moyen: {df_summary['theta_std'].mean():.4f}")
    print(f"  Plage: [{df_summary['theta_min'].min():.4f}, {df_summary['theta_max'].max():.4f}]")

    # Statistiques Gini
    print("\n📊 Coefficient de Gini:")
    print(f"  Gini moyen global: {df_summary['gini_mean'].mean():.4f} ± {df_summary['gini_mean'].std():.4f}")
    print(f"  Gini final moyen: {df_summary['gini_final'].mean():.4f}")

    # Catastrophes
    if 'catastrophes_total' in df_summary.columns:
        print("\n📊 Catastrophes:")
        print(f"  Total catastrophes: {df_summary['catastrophes_total'].sum()}")
        print(f"  Moyenne par scénario: {df_summary['catastrophes_total'].mean():.1f}")

    # Population
    print("\n📊 Population:")
    print(f"  Population finale moyenne: {df_summary['population_final'].mean():.0f}")
    print(f"  Variation: {df_summary['population_final'].std():.0f}")

    # Régulation
    print("\n📊 Régulation:")
    print(f"  C2 activations moyennes: {df_summary['C2_activations'].mean():.1f}")
    print(f"  C3 activations moyennes: {df_summary['C3_activations'].mean():.1f}")

    # Effet des paramètres
    print("\n📊 Effet des paramètres:")

    # Catastrophes ON/OFF
    if 'enable_catastrophes' in df_summary.columns:
        with_cata = df_summary[df_summary['enable_catastrophes'] == True]
        without_cata = df_summary[df_summary['enable_catastrophes'] == False]
        print(f"  Catastrophes ON:  θ_std={with_cata['theta_std'].mean():.4f}, "
              f"Gini={with_cata['gini_final'].mean():.3f}")
        print(f"  Catastrophes OFF: θ_std={without_cata['theta_std'].mean():.4f}, "
              f"Gini={without_cata['gini_final'].mean():.3f}")

    # Conservation rate
    if 'conservation_rate' in df_summary.columns:
        for rho in sorted(df_summary['conservation_rate'].unique()):
            subset = df_summary[df_summary['conservation_rate'] == rho]
            print(f"  ρ={rho:.2f}: θ_std={subset['theta_std'].mean():.4f}, "
                  f"Gini={subset['gini_final'].mean():.3f}")

    print("\n" + "="*80 + "\n")


def main():
    """Point d'entrée principal du programme."""
    # Vérification du répertoire de travail
    if not Path("iris/core").exists():
        print("❌ ERREUR: Ce script doit être exécuté depuis la racine du projet")
        print("   Usage: python -m iris.simulations.experiment_grid")
        sys.exit(1)

    # Lancement de la grille d'expériences
    output_dir = Path("results/grid")
    df_summary = run_all_grid(output_dir)

    # Affichage des statistiques
    print_summary_statistics(df_summary)

    print("✅ Toutes les expériences sont terminées.")
    print(f"📁 Résultats disponibles dans: {output_dir.absolute()}")
    print(f"📊 Résumé global: {output_dir / 'summary.csv'}")


if __name__ == "__main__":
    main()
