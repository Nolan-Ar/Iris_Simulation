"""
IRIS Economic System - Scenario Testing
========================================

Scénarios de test pour évaluer la résilience du système IRIS.

Auteur: Arnault Nolan
Email: arnaultnolan@gmail.com
Date: 2025

Scénarios implémentés :
1. Baseline (fonctionnement normal)
2. Choc de richesse (destruction d'actifs)
3. Choc de demande (augmentation soudaine de liquidité)
4. Choc d'offre (perturbation de la production)
5. Crise systémique (combinaison de chocs)
6. Comparaison avec système traditionnel (sans régulation)
"""

import numpy as np
from typing import Dict, List
from .iris_model import IRISEconomy
from ..analysis.iris_visualizer import IRISVisualizer


class ScenarioRunner:
    """Classe pour exécuter et comparer différents scénarios"""

    def __init__(self, n_agents: int = 100, output_dir: str = "results"):
        """
        Initialise le gestionnaire de scénarios

        Args:
            n_agents: Nombre d'agents dans chaque simulation
            output_dir: Répertoire de sortie
        """
        self.n_agents = n_agents
        self.output_dir = output_dir
        self.results: Dict[str, Dict] = {}

    def run_baseline(self, steps: int = 1000) -> IRISEconomy:
        """
        Scénario baseline : fonctionnement normal du système

        Args:
            steps: Durée de la simulation

        Returns:
            Économie IRIS après simulation
        """
        print("\n" + "="*70)
        print("SCÉNARIO 1 : BASELINE - Fonctionnement Normal")
        print("="*70)

        economy = IRISEconomy(
            initial_agents=self.n_agents,
            gold_factor=1.0,
            universal_income_rate=0.01
        )

        economy.simulate(steps=steps, n_transactions=20)

        self.results['baseline'] = economy.history

        print(f"\n📈 Résultats baseline :")
        print(f"  Thermomètre final : {economy.thermometer():.4f}")
        print(f"  Indicateur final : {economy.indicator():.4f}")
        print(f"  Gini final : {economy.gini_coefficient():.4f}")

        return economy

    def run_wealth_loss_shock(self, steps: int = 1000,
                              shock_time: int = 500,
                              magnitude: float = 0.3) -> IRISEconomy:
        """
        Scénario de choc de richesse : destruction d'une partie du patrimoine
        (catastrophe naturelle, guerre, crise financière)

        Args:
            steps: Durée de la simulation
            shock_time: Moment du choc
            magnitude: Proportion de richesse détruite (0-1)

        Returns:
            Économie IRIS après simulation
        """
        print("\n" + "="*70)
        print(f"SCÉNARIO 2 : CHOC DE RICHESSE - Perte de {magnitude*100:.0f}% du patrimoine")
        print("="*70)

        economy = IRISEconomy(
            initial_agents=self.n_agents,
            gold_factor=1.0,
            universal_income_rate=0.01
        )

        # Phase pré-choc
        print(f"\nPhase 1 : Stabilisation initiale ({shock_time} pas)...")
        for _ in range(shock_time):
            economy.step(n_transactions=20)

        # Injection du choc
        economy.inject_shock('wealth_loss', magnitude)

        # Phase post-choc
        print(f"\nPhase 2 : Récupération post-choc ({steps - shock_time} pas)...")
        for _ in range(steps - shock_time):
            economy.step(n_transactions=20)
            if (economy.time) % 100 == 0:
                theta = economy.thermometer()
                indicator = economy.indicator()
                print(f"  Pas {economy.time}/{steps} - θ={theta:.4f}, I={indicator:.4f}")

        self.results[f'wealth_loss_{int(magnitude*100)}'] = economy.history

        print(f"\n📈 Résultats après choc de richesse :")
        print(f"  Thermomètre final : {economy.thermometer():.4f}")
        print(f"  Indicateur final : {economy.indicator():.4f}")
        print(f"  Temps de récupération : {self._compute_recovery_time(economy.history, shock_time)} pas")

        return economy

    def run_demand_surge_shock(self, steps: int = 1000,
                               shock_time: int = 500,
                               magnitude: float = 0.5) -> IRISEconomy:
        """
        Scénario de choc de demande : augmentation soudaine de la liquidité
        (conversion massive V -> U, ruée bancaire inverse)

        Args:
            steps: Durée de la simulation
            shock_time: Moment du choc
            magnitude: Proportion de V converti en U

        Returns:
            Économie IRIS après simulation
        """
        print("\n" + "="*70)
        print(f"SCÉNARIO 3 : CHOC DE DEMANDE - Conversion massive {magnitude*100:.0f}% V→U")
        print("="*70)

        economy = IRISEconomy(
            initial_agents=self.n_agents,
            gold_factor=1.0,
            universal_income_rate=0.01
        )

        # Phase pré-choc
        print(f"\nPhase 1 : Stabilisation initiale ({shock_time} pas)...")
        for _ in range(shock_time):
            economy.step(n_transactions=20)

        # Injection du choc
        economy.inject_shock('demand_surge', magnitude)

        # Phase post-choc
        print(f"\nPhase 2 : Régulation post-choc ({steps - shock_time} pas)...")
        for _ in range(steps - shock_time):
            economy.step(n_transactions=20)
            if (economy.time) % 100 == 0:
                theta = economy.thermometer()
                kappa = economy.rad.kappa
                print(f"  Pas {economy.time}/{steps} - θ={theta:.4f}, κ={kappa:.4f}")

        self.results[f'demand_surge_{int(magnitude*100)}'] = economy.history

        print(f"\n📈 Résultats après choc de demande :")
        print(f"  Thermomètre final : {economy.thermometer():.4f}")
        print(f"  Coefficient κ final : {economy.rad.kappa:.4f}")
        print(f"  Taux de circulation U/V : {economy.circulation_rate():.4f}")

        return economy

    def run_supply_shock(self, steps: int = 1000,
                        shock_time: int = 500,
                        magnitude: float = 2.0) -> IRISEconomy:
        """
        Scénario de choc d'offre : augmentation des coûts de transaction
        (crise énergétique, inflation des coûts)

        Args:
            steps: Durée de la simulation
            shock_time: Moment du choc
            magnitude: Multiplicateur du taux de dissipation

        Returns:
            Économie IRIS après simulation
        """
        print("\n" + "="*70)
        print(f"SCÉNARIO 4 : CHOC D'OFFRE - Augmentation dissipation ×{magnitude:.1f}")
        print("="*70)

        economy = IRISEconomy(
            initial_agents=self.n_agents,
            gold_factor=1.0,
            universal_income_rate=0.01
        )

        # Phase pré-choc
        print(f"\nPhase 1 : Stabilisation initiale ({shock_time} pas)...")
        for _ in range(shock_time):
            economy.step(n_transactions=20)

        dissipation_before = economy.rad.dissipation_rate

        # Injection du choc
        economy.inject_shock('supply_shock', magnitude)

        print(f"  Dissipation avant : {dissipation_before:.4f}")
        print(f"  Dissipation après : {economy.rad.dissipation_rate:.4f}")

        # Phase post-choc
        print(f"\nPhase 2 : Adaptation post-choc ({steps - shock_time} pas)...")
        for _ in range(steps - shock_time):
            economy.step(n_transactions=20)
            if (economy.time) % 100 == 0:
                theta = economy.thermometer()
                dissip = economy.rad.dissipation_rate
                print(f"  Pas {economy.time}/{steps} - θ={theta:.4f}, dissipation={dissip:.4f}")

        self.results[f'supply_shock_{int(magnitude*10)}'] = economy.history

        print(f"\n📈 Résultats après choc d'offre :")
        print(f"  Thermomètre final : {economy.thermometer():.4f}")
        print(f"  Dissipation finale : {economy.rad.dissipation_rate:.4f}")

        return economy

    def run_systemic_crisis(self, steps: int = 1500) -> IRISEconomy:
        """
        Scénario de crise systémique : combinaison de plusieurs chocs successifs

        Args:
            steps: Durée de la simulation

        Returns:
            Économie IRIS après simulation
        """
        print("\n" + "="*70)
        print("SCÉNARIO 5 : CRISE SYSTÉMIQUE - Chocs multiples")
        print("="*70)

        economy = IRISEconomy(
            initial_agents=self.n_agents,
            gold_factor=1.0,
            universal_income_rate=0.01
        )

        # Phase 1 : Stabilisation
        phase1 = 300
        print(f"\nPhase 1 : Stabilisation ({phase1} pas)...")
        for _ in range(phase1):
            economy.step(n_transactions=20)

        # Choc 1 : Perte de richesse
        print(f"\nATTENTION: CHOC 1 - Destruction de patrimoine (t={economy.time})")
        economy.inject_shock('wealth_loss', 0.25)

        # Phase 2 : Récupération partielle
        phase2 = 300
        print(f"\nPhase 2 : Récupération ({phase2} pas)...")
        for _ in range(phase2):
            economy.step(n_transactions=20)

        # Choc 2 : Choc de demande
        print(f"\nATTENTION: CHOC 2 - Panique et conversion massive V→U (t={economy.time})")
        economy.inject_shock('demand_surge', 0.6)

        # Phase 3 : Régulation
        phase3 = 400
        print(f"\nPhase 3 : Régulation ({phase3} pas)...")
        for _ in range(phase3):
            economy.step(n_transactions=20)
            if (economy.time) % 100 == 0:
                theta = economy.thermometer()
                indicator = economy.indicator()
                kappa = economy.rad.kappa
                print(f"  Pas {economy.time}/{steps} - θ={theta:.4f}, I={indicator:.4f}, κ={kappa:.4f}")

        # Choc 3 : Choc d'offre
        print(f"\nATTENTION: CHOC 3 - Crise énergétique (t={economy.time})")
        economy.inject_shock('supply_shock', 2.5)

        # Phase 4 : Stabilisation finale
        remaining = steps - economy.time
        print(f"\nPhase 4 : Stabilisation finale ({remaining} pas)...")
        for _ in range(remaining):
            economy.step(n_transactions=20)
            if (economy.time) % 100 == 0:
                theta = economy.thermometer()
                indicator = economy.indicator()
                print(f"  Pas {economy.time}/{steps} - θ={theta:.4f}, I={indicator:.4f}")

        self.results['systemic_crisis'] = economy.history

        print(f"\n📈 Résultats après crise systémique :")
        print(f"  Thermomètre final : {economy.thermometer():.4f}")
        print(f"  Indicateur final : {economy.indicator():.4f}")
        print(f"  Système stable : {abs(economy.indicator()) < 0.1}")

        return economy

    def run_comparison_no_regulation(self, steps: int = 1000,
                                     shock_time: int = 500,
                                     shock_type: str = 'wealth_loss',
                                     magnitude: float = 0.3) -> IRISEconomy:
        """
        Scénario de comparaison : système sans régulation automatique
        (κ fixe, pas de rétroaction)

        Args:
            steps: Durée de la simulation
            shock_time: Moment du choc
            shock_type: Type de choc
            magnitude: Intensité du choc

        Returns:
            Économie IRIS sans régulation
        """
        print("\n" + "="*70)
        print("SCÉNARIO 6 : SYSTÈME SANS RÉGULATION (témoin)")
        print("="*70)

        economy = IRISEconomy(
            initial_agents=self.n_agents,
            gold_factor=1.0,
            universal_income_rate=0.01
        )

        # Désactive la régulation en fixant kappa
        original_kappa = economy.rad.kappa

        # Phase pré-choc
        print(f"\nPhase 1 : Avant choc ({shock_time} pas)...")
        for _ in range(shock_time):
            # Pas de régulation : kappa reste fixe
            economy.step(n_transactions=20)
            economy.rad.kappa = original_kappa  # Force kappa constant

        # Injection du choc
        print(f"\nATTENTION: Choc : {shock_type} (magnitude={magnitude})")
        economy.inject_shock(shock_type, magnitude)

        # Phase post-choc sans régulation
        print(f"\nPhase 2 : Après choc SANS régulation ({steps - shock_time} pas)...")
        for _ in range(steps - shock_time):
            economy.step(n_transactions=20)
            economy.rad.kappa = original_kappa  # Force kappa constant
            if (economy.time) % 100 == 0:
                theta = economy.thermometer()
                indicator = economy.indicator()
                print(f"  Pas {economy.time}/{steps} - θ={theta:.4f}, I={indicator:.4f}")

        self.results['no_regulation'] = economy.history

        print(f"\n📈 Résultats sans régulation :")
        print(f"  Thermomètre final : {economy.thermometer():.4f}")
        print(f"  Indicateur final : {economy.indicator():.4f}")
        print(f"  ATTENTION: Déviation importante : {abs(economy.indicator()) > 0.1}")

        return economy

    def _compute_recovery_time(self, history: Dict, shock_time: int,
                              threshold: float = 0.05) -> int:
        """
        Calcule le temps de récupération après un choc

        Args:
            history: Historique de simulation
            shock_time: Moment du choc
            threshold: Seuil de retour à l'équilibre

        Returns:
            Nombre de pas pour revenir à l'équilibre
        """
        indicator = np.array(history['indicator'])

        # Cherche le premier moment après le choc où |I| < threshold
        post_shock = indicator[shock_time:]

        for i, val in enumerate(post_shock):
            if abs(val) < threshold:
                return i

        return len(post_shock)  # Pas revenu à l'équilibre

    def compare_scenarios(self, shock_time: int = 500):
        """
        Génère des visualisations comparatives de tous les scénarios

        Args:
            shock_time: Moment du choc (pour les graphiques)
        """
        if not self.results:
            print("ATTENTION: Aucun scénario n'a été exécuté. Lancez d'abord les scénarios.")
            return

        viz = IRISVisualizer(self.output_dir)

        print("\nGénération des comparaisons visuelles...")

        # Graphique de comparaison des chocs
        viz.plot_shock_comparison(self.results, shock_time)

        print("OK: Visualisations comparatives générées")

    def generate_comparative_report(self):
        """
        Génère un rapport comparatif de tous les scénarios
        """
        if not self.results:
            print("ATTENTION: Aucun résultat à rapporter.")
            return

        print("\n" + "="*70)
        print("RAPPORT COMPARATIF - Résilience du Système IRIS")
        print("="*70 + "\n")

        for scenario_name, history in self.results.items():
            theta_array = np.array(history['thermometer'])
            indicator_array = np.array(history['indicator'])
            gini_array = np.array(history['gini_coefficient'])

            print(f"\n{scenario_name.upper()}")
            print(f"  {'─'*60}")
            print(f"  Thermomètre moyen : {theta_array.mean():.4f} ± {theta_array.std():.4f}")
            print(f"  Indicateur moyen : {indicator_array.mean():.4f} ± {indicator_array.std():.4f}")
            print(f"  Gini final : {gini_array[-1]:.4f}")
            print(f"  Stabilité (95% déviations) : {np.percentile(np.abs(indicator_array), 95):.4f}")

            # Évaluation de la résilience
            max_deviation = np.max(np.abs(indicator_array))
            if max_deviation < 0.1:
                resilience = "🟢 EXCELLENTE"
            elif max_deviation < 0.2:
                resilience = "🟡 BONNE"
            elif max_deviation < 0.5:
                resilience = "🟠 MOYENNE"
            else:
                resilience = "🔴 FAIBLE"

            print(f"  Résilience : {resilience} (déviation max = {max_deviation:.4f})")

        print("\n" + "="*70 + "\n")


def run_full_analysis(n_agents: int = 100, output_dir: str = "results",
                     steps: int = 1000, shock_time: int = 500, seed: int = None):
    """
    Execute l'analyse complete avec tous les scenarios

    Args:
        n_agents: Nombre d'agents
        output_dir: Repertoire de sortie
        steps: Nombre de pas de temps pour chaque scenario
        shock_time: Moment du choc pour les scenarios de choc
        seed: Graine aleatoire pour reproductibilite (None = aleatoire)
    """
    # Fixe la graine si specifiee (pour reproductibilite)
    if seed is not None:
        np.random.seed(seed)
        print(f"Graine aleatoire fixee : {seed}")

    runner = ScenarioRunner(n_agents=n_agents, output_dir=output_dir)

    # Scenario 1 : Baseline
    economy_baseline = runner.run_baseline(steps=steps)

    # Scenario 2 : Choc de richesse modere
    economy_wealth_loss = runner.run_wealth_loss_shock(
        steps=steps, shock_time=shock_time, magnitude=0.3
    )

    # Scenario 3 : Choc de demande important
    economy_demand = runner.run_demand_surge_shock(
        steps=steps, shock_time=shock_time, magnitude=0.5
    )

    # Scenario 4 : Choc d'offre
    economy_supply = runner.run_supply_shock(
        steps=steps, shock_time=shock_time, magnitude=2.0
    )

    # Scenario 5 : Crise systemique
    economy_crisis = runner.run_systemic_crisis(steps=int(steps * 1.5))

    # Scenario 6 : Systeme sans regulation (temoin)
    economy_no_reg = runner.run_comparison_no_regulation(
        steps=steps, shock_time=shock_time, shock_type='wealth_loss', magnitude=0.3
    )

    # Comparaisons et rapports
    runner.compare_scenarios(shock_time=shock_time)
    runner.generate_comparative_report()

    # Visualisations individuelles detaillees
    viz = IRISVisualizer(output_dir)

    print("\nGénération des visualisations détaillées...")
    viz.plot_main_variables(economy_baseline.history, "Scénario_1_Baseline")
    viz.plot_main_variables(economy_crisis.history, "Scénario_5_Crise_Systémique")
    viz.plot_regulation_detail(economy_baseline.history)
    viz.plot_phase_space(economy_baseline.history)

    # Export des données
    for scenario_name, history in runner.results.items():
        viz.export_data(history, f"data_{scenario_name}")

    print("\n✅ ANALYSE COMPLÈTE TERMINÉE")
    print(f"📁 Résultats disponibles dans : {output_dir}/")

    return runner
