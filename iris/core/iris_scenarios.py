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
7. Regulation Only (mécanismes de régulation pure - pour illustration théorique)
8. Baseline Stable (équilibre stable avec paramètres par défaut)
9. Crisis High Volatility (stress test avec volatilité élevée)
10. No Regulation (système sans RAD, η=κ=1 fixes)
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

    def run_regulation_only(self, steps: int = 1000) -> IRISEconomy:
        """
        Scénario REGULATION ONLY : Mécanismes de régulation pure

        ═══════════════════════════════════════════════════════════════════════════
        MODE "RÉGULATION PURE" - POUR ILLUSTRATION THÉORIQUE
        ═══════════════════════════════════════════════════════════════════════════

        Ce scénario désactive TOUS les modules complexes pour ne garder que :
        - Les variables fondamentales : V_circ, D, θ (thermomètre)
        - Les mécanismes de régulation : κ (kappa), η (eta)
        - Le revenu universel : RU = κ × (V_on × τ) / N
        - Les capteurs : r_ic, ν_eff

        MODULES DÉSACTIVÉS :
        - ❌ Démographie (naissances/décès)
        - ❌ Catastrophes aléatoires
        - ❌ Prix dynamiques
        - ❌ Entreprises dynamiques (créations/faillites)
        - ❌ Combustion des entreprises (S+U→V)
        - ❌ Chambre de Relance

        OBJECTIF :
        Illustrer le mécanisme de régulation contracyclique pur pour un chapitre
        de thèse sans la complexité des modules annexes.

        Le système montre comment :
        1. κ régule la liquidité (conversion V→U + montant RU)
        2. θ = D/V_on mesure la tension thermodynamique
        3. Le RAD maintient θ proche de 1 (équilibre)

        Args:
            steps: Durée de la simulation (en mois)

        Returns:
            Économie IRIS après simulation (mode régulation pure)
        """
        print("\n" + "="*70)
        print("SCÉNARIO : REGULATION ONLY - Mécanismes de Régulation Pure")
        print("="*70)
        print("\n📌 MODE RÉGULATION PURE (pour illustration théorique)")
        print("   Modules actifs : V, U, D, θ, κ, η, RU, r_ic, ν_eff")
        print("   Modules désactivés : démographie, catastrophes, prix, entreprises\n")

        # Création de l'économie avec TOUS les modules complexes désactivés
        economy = IRISEconomy(
            initial_agents=self.n_agents,
            gold_factor=1.0,
            universal_income_rate=0.01,
            # ═══════════════════════════════════════════════════════════════
            # DÉSACTIVATION DE TOUS LES MODULES COMPLEXES
            # ═══════════════════════════════════════════════════════════════
            enable_demographics=False,           # Pas de naissances/décès
            enable_catastrophes=False,           # Pas de chocs aléatoires
            enable_price_discovery=False,        # Pas de prix dynamiques
            enable_dynamic_business=False,       # Pas de créations/faillites
            enable_business_combustion=False,    # Pas de production entreprise
            enable_chambre_relance=False,        # Pas de redistribution CR
        )

        print(f"Simulation de {steps} steps (mois) en mode régulation pure...")
        economy.simulate(steps=steps, n_transactions=20)

        self.results['regulation_only'] = economy.history

        # Analyse des résultats
        print(f"\n📈 Résultats (mode régulation pure) :")
        print(f"  Thermomètre final (θ) : {economy.thermometer():.4f}")
        print(f"  Indicateur final (I) : {economy.indicator():.4f}")
        print(f"  Kappa final (κ) : {economy.rad.kappa:.4f}")
        print(f"  Eta final (η) : {economy.rad.eta:.4f}")
        print(f"  Gini final : {economy.gini_coefficient():.4f}")

        # Vérification de la stabilité
        theta_history = np.array(economy.history['thermometer'])
        if len(theta_history) > 0:
            theta_mean = np.mean(theta_history)
            theta_std = np.std(theta_history)
            print(f"\n  Stabilité du thermomètre :")
            print(f"    Moyenne : {theta_mean:.4f}")
            print(f"    Écart-type : {theta_std:.4f}")

            # Convergence vers l'équilibre ?
            if abs(theta_mean - 1.0) < 0.1 and theta_std < 0.2:
                print(f"    ✓ Le système converge vers l'équilibre (θ ≈ 1)")
            else:
                print(f"    ⚠ Le système s'éloigne de l'équilibre")

        print("\n" + "="*70 + "\n")

        return economy

    def run_baseline_stable(self, steps: int = 1200) -> IRISEconomy:
        """
        Scénario BASELINE STABLE : Équilibre stable avec paramètres par défaut

        ═══════════════════════════════════════════════════════════════════════════
        SCÉNARIO BASELINE STABLE - DÉMONSTRATION D'ÉQUILIBRE
        ═══════════════════════════════════════════════════════════════════════════

        Ce scénario illustre le fonctionnement stable du système IRIS en conditions
        normales avec tous les modules activés et les paramètres par défaut.

        OBJECTIF :
        Démontrer la capacité du système à maintenir l'équilibre thermodynamique
        (θ ≈ 1) sur le long terme sans chocs externes, grâce à la régulation
        contracyclique automatique du RAD.

        MODULES ACTIFS :
        - ✅ Démographie (naissances/décès réalistes)
        - ✅ Entreprises dynamiques (créations/faillites)
        - ✅ Combustion S+U→V (production)
        - ✅ Chambre de Relance
        - ✅ Régulation RAD (κ, η contracycliques)
        - ✅ Revenu Universel (RU modulé par κ)
        - ❌ Catastrophes (désactivées pour stabilité)

        PARAMÈTRES NOTABLES :
        - universal_income_rate = 0.02 (2% de V_on distribué/an)
        - kappa_smoothing = 0.1 (lissage modéré)
        - eta_smoothing = 0.15 (lissage modéré)
        - Durée recommandée : 1200 steps (100 ans)

        CE QU'ON OBSERVE :
        1. Thermomètre θ oscille doucement autour de 1.0 (±0.1)
        2. κ et η s'ajustent de manière contracyclique
        3. Population croît de manière réaliste
        4. Entreprises naissent et meurent naturellement
        5. Inégalités (Gini) restent modérées grâce au RU

        Args:
            steps: Durée de la simulation en mois (défaut: 1200 = 100 ans)

        Returns:
            Économie IRIS après simulation (état stable)
        """
        print("\n" + "="*70)
        print("SCÉNARIO 8 : BASELINE STABLE - Équilibre à Long Terme")
        print("="*70)
        print("\n📌 OBJECTIF : Démontrer la stabilité naturelle du système IRIS")
        print("   Modules actifs : Tous (sauf catastrophes)")
        print("   Paramètres : Par défaut (calibrés pour stabilité)\n")

        # Création de l'économie avec paramètres optimaux pour stabilité
        economy = IRISEconomy(
            initial_agents=self.n_agents,
            gold_factor=1.0,
            universal_income_rate=0.02,  # 2% RU annuel
            # ═══════════════════════════════════════════════════════════════
            # CONFIGURATION POUR STABILITÉ MAXIMALE
            # ═══════════════════════════════════════════════════════════════
            enable_demographics=True,             # Démographie réaliste
            enable_catastrophes=False,            # Pas de chocs externes
            enable_price_discovery=True,          # Prix dynamiques
            enable_dynamic_business=True,         # Entreprises évolutives
            enable_business_combustion=True,      # Production active
            enable_chambre_relance=True,          # Redistribution
        )

        # Affichage initial
        print(f"État initial :")
        print(f"  Population : {len(economy.agents)} agents")
        print(f"  V_on initial : {economy.get_V_on():.0f}")
        print(f"  D total initial : {economy.rad.total_D():.0f}")
        print(f"  Thermomètre θ : {economy.thermometer():.4f}")

        # Simulation longue durée
        print(f"\nSimulation de {steps} steps ({steps//12} ans)...")
        economy.simulate(steps=steps, n_transactions=20)

        self.results['baseline_stable'] = economy.history

        # Analyse de la stabilité
        theta_history = np.array(economy.history['thermometer'])
        indicator_history = np.array(economy.history['indicator'])
        kappa_history = np.array(economy.history.get('kappa', [1.0] * len(theta_history)))

        theta_mean = np.mean(theta_history)
        theta_std = np.std(theta_history)
        indicator_mean = np.mean(indicator_history)
        indicator_std = np.std(indicator_history)

        print(f"\n📈 Résultats (baseline stable) :")
        print(f"  ═══════════════════════════════════════════════════════════")
        print(f"  STABILITÉ THERMODYNAMIQUE :")
        print(f"    Thermomètre θ moyen : {theta_mean:.4f} (cible = 1.0)")
        print(f"    Écart-type θ : {theta_std:.4f}")
        print(f"    Thermomètre θ final : {economy.thermometer():.4f}")
        print(f"  ═══════════════════════════════════════════════════════════")
        print(f"  RÉGULATION CONTRACYCLIQUE :")
        print(f"    Indicateur I moyen : {indicator_mean:.4f} (cible = 0.0)")
        print(f"    Écart-type I : {indicator_std:.4f}")
        print(f"    Kappa κ final : {economy.rad.kappa:.4f}")
        print(f"    Eta η final : {economy.rad.eta:.4f}")
        print(f"  ═══════════════════════════════════════════════════════════")
        print(f"  MÉTRIQUES ÉCONOMIQUES :")
        print(f"    Population finale : {len(economy.agents)} agents")
        print(f"    V_on final : {economy.get_V_on():.0f}")
        print(f"    Coefficient Gini : {economy.gini_coefficient():.4f}")
        print(f"  ═══════════════════════════════════════════════════════════")

        # Évaluation de la stabilité
        if abs(theta_mean - 1.0) < 0.1 and theta_std < 0.2:
            print(f"  ✅ SYSTÈME STABLE : θ converge vers l'équilibre")
        else:
            print(f"  ⚠️  SYSTÈME INSTABLE : déviation significative de θ")

        print("\n" + "="*70 + "\n")

        return economy

    def run_crisis_high_volatility(self, steps: int = 600) -> IRISEconomy:
        """
        Scénario CRISIS HIGH VOLATILITY : Stress test avec volatilité élevée

        ═══════════════════════════════════════════════════════════════════════════
        SCÉNARIO CRISIS HIGH VOLATILITY - TEST DE RÉSILIENCE
        ═══════════════════════════════════════════════════════════════════════════

        Ce scénario teste la résilience du système IRIS face à des conditions
        extrêmes : catastrophes fréquentes, régulation hyper-réactive, volatilité
        maximale. Objectif : vérifier que le RAD maintient la stabilité même sous
        stress intense.

        OBJECTIF :
        Démontrer la robustesse du système IRIS face à des chocs multiples et
        une volatilité économique élevée. Évaluer les limites de la régulation
        contracyclique en conditions extrêmes.

        MODULES ACTIFS :
        - ✅ Démographie (avec wealth_influence pour amplifier effets)
        - ✅ Catastrophes (TOUTES, fréquence élevée)
        - ✅ Entreprises dynamiques (créations/faillites rapides)
        - ✅ Combustion et Chambre de Relance
        - ✅ Régulation RAD (paramètres ultra-réactifs)

        PARAMÈTRES MODIFIÉS POUR HAUTE VOLATILITÉ :
        - Catastrophes : base_frequency = 0.20 (20% probabilité/an vs 5% normal)
        - RAD : kappa_smoothing = 0.3 (réaction rapide vs 0.1 normal)
        - RAD : eta_smoothing = 0.4 (réaction rapide vs 0.15 normal)
        - RAD : kappa_beta = 0.8 (haute sensibilité vs 0.5 normal)
        - RAD : eta_alpha = 0.8 (haute sensibilité vs 0.5 normal)

        CE QU'ON OBSERVE :
        1. Thermomètre θ fluctue fortement (±0.3 à ±0.5)
        2. κ et η réagissent rapidement et fortement
        3. Catastrophes fréquentes créent des chocs de D
        4. Population et entreprises volatiles
        5. Le système SE STABILISE malgré la volatilité (preuve de résilience)

        Args:
            steps: Durée de la simulation en mois (défaut: 600 = 50 ans)

        Returns:
            Économie IRIS après simulation (état post-crise)
        """
        print("\n" + "="*70)
        print("SCÉNARIO 9 : CRISIS HIGH VOLATILITY - Stress Test Extrême")
        print("="*70)
        print("\n📌 OBJECTIF : Tester les limites de résilience du système IRIS")
        print("   Conditions : Catastrophes fréquentes, régulation hyper-réactive")
        print("   Attente : Le RAD maintient la stabilité malgré la volatilité\n")

        # Création de l'économie avec paramètres de haute volatilité
        economy = IRISEconomy(
            initial_agents=self.n_agents,
            gold_factor=1.0,
            universal_income_rate=0.02,
            # ═══════════════════════════════════════════════════════════════
            # CONFIGURATION HAUTE VOLATILITÉ
            # ═══════════════════════════════════════════════════════════════
            enable_demographics=True,
            enable_catastrophes=True,             # CATASTROPHES ACTIVÉES
            enable_price_discovery=True,
            enable_dynamic_business=True,
            enable_business_combustion=True,
            enable_chambre_relance=True,
        )

        # Modification des paramètres RAD pour réactivité élevée
        economy.rad.kappa_smoothing = 0.3        # Réaction rapide (vs 0.1 normal)
        economy.rad.eta_smoothing = 0.4          # Réaction rapide (vs 0.15 normal)
        economy.rad.kappa_beta = 0.8             # Haute sensibilité (vs 0.5 normal)
        economy.rad.eta_alpha = 0.8              # Haute sensibilité (vs 0.5 normal)

        # Configuration catastrophes pour haute fréquence
        if hasattr(economy, 'catastrophe_manager') and economy.catastrophe_manager:
            economy.catastrophe_manager.base_frequency = 0.20  # 20% vs 5% normal

        # Affichage initial
        print(f"État initial :")
        print(f"  Population : {len(economy.agents)} agents")
        print(f"  θ initial : {economy.thermometer():.4f}")
        print(f"\n⚡ PARAMÈTRES DE VOLATILITÉ :")
        print(f"  Catastrophes : 20% probabilité/an (4× normale)")
        print(f"  Régulation RAD : réactivité maximale (κ_smooth=0.3, η_smooth=0.4)")
        print(f"  Sensibilité : β=α=0.8 (1.6× normale)")

        # Simulation sous stress
        print(f"\nSimulation de {steps} steps ({steps//12} ans) sous stress...")
        print("⚠️  Attendez-vous à de fortes fluctuations...")

        economy.simulate(steps=steps, n_transactions=20)

        self.results['crisis_high_volatility'] = economy.history

        # Analyse de la résilience
        theta_history = np.array(economy.history['thermometer'])
        indicator_history = np.array(economy.history['indicator'])

        theta_mean = np.mean(theta_history)
        theta_std = np.std(theta_history)
        theta_max_dev = np.max(np.abs(theta_history - 1.0))
        indicator_max = np.max(np.abs(indicator_history))

        # Calcul du temps de récupération après chocs
        large_deviations = np.where(np.abs(indicator_history) > 0.3)[0]
        n_large_deviations = len(large_deviations)

        print(f"\n📈 Résultats (crisis high volatility) :")
        print(f"  ═══════════════════════════════════════════════════════════")
        print(f"  VOLATILITÉ OBSERVÉE :")
        print(f"    Thermomètre θ moyen : {theta_mean:.4f}")
        print(f"    Écart-type θ : {theta_std:.4f} (↑ volatilité)")
        print(f"    Déviation max |θ - 1| : {theta_max_dev:.4f}")
        print(f"    Indicateur I max : {indicator_max:.4f}")
        print(f"  ═══════════════════════════════════════════════════════════")
        print(f"  RÉSILIENCE DU SYSTÈME :")
        print(f"    Nombre de déviations |I| > 0.3 : {n_large_deviations}")
        print(f"    Thermomètre final : {economy.thermometer():.4f}")
        print(f"    Kappa κ final : {economy.rad.kappa:.4f}")
        print(f"    Eta η final : {economy.rad.eta:.4f}")
        print(f"  ═══════════════════════════════════════════════════════════")
        print(f"  ÉTAT FINAL :")
        print(f"    Population : {len(economy.agents)} agents")
        print(f"    Gini : {economy.gini_coefficient():.4f}")
        print(f"  ═══════════════════════════════════════════════════════════")

        # Évaluation de la résilience
        if theta_std < 0.5 and abs(theta_mean - 1.0) < 0.2:
            print(f"  ✅ SYSTÈME RÉSILIENT : Maintient stabilité malgré volatilité")
        elif theta_std < 1.0:
            print(f"  🟡 SYSTÈME PARTIELLEMENT RÉSILIENT : Fluctuations maîtrisées")
        else:
            print(f"  ⚠️  SYSTÈME INSTABLE : Volatilité excessive")

        print("\n" + "="*70 + "\n")

        return economy

    def run_no_regulation(self, steps: int = 1000) -> IRISEconomy:
        """
        Scénario NO REGULATION : Système sans régulation RAD (η=κ=1 fixes)

        ═══════════════════════════════════════════════════════════════════════════
        SCÉNARIO NO REGULATION - TÉMOIN SANS RAD
        ═══════════════════════════════════════════════════════════════════════════

        Ce scénario désactive complètement la régulation automatique du RAD en
        fixant κ=η=1 constants. Il sert de TÉMOIN pour comparer avec les scénarios
        régulés et démontrer l'apport de la régulation contracyclique.

        OBJECTIF :
        Démontrer l'importance critique du RAD en montrant qu'un système SANS
        régulation contracyclique diverge de l'équilibre et accumule des
        déséquilibres thermodynamiques (θ s'éloigne de 1).

        MODULES ACTIFS :
        - ✅ Démographie
        - ✅ Entreprises dynamiques
        - ✅ Combustion et Chambre de Relance
        - ❌ Régulation RAD : κ=η=1 FIXES (pas d'ajustement contracyclique)
        - ❌ Catastrophes (pour isoler l'effet de la non-régulation)

        PARAMÈTRES FIGÉS :
        - κ (kappa) = 1.0 CONSTANT (pas de modulation de liquidité)
        - η (eta) = 1.0 CONSTANT (pas de modulation de production)
        - Pas de mise à jour de κ et η par le RAD
        - RU = (V_on × τ) / N sans modulation par κ

        CE QU'ON OBSERVE (ATTENDU) :
        1. Thermomètre θ dérive progressivement (ne reste pas proche de 1)
        2. Indicateur I s'accumule (déséquilibre croissant)
        3. Pas de mécanisme de rééquilibrage automatique
        4. Instabilités structurelles à long terme
        5. CONTRASTE fort avec scénarios régulés

        COMPARAISON RECOMMANDÉE :
        - Comparer avec run_baseline_stable() pour voir l'effet du RAD
        - Observer θ(t) : avec RAD → oscille autour de 1, sans RAD → dérive

        Args:
            steps: Durée de la simulation en mois (défaut: 1000 ≈ 83 ans)

        Returns:
            Économie IRIS sans régulation (pour comparaison)
        """
        print("\n" + "="*70)
        print("SCÉNARIO 10 : NO REGULATION - Témoin Sans RAD")
        print("="*70)
        print("\n📌 OBJECTIF : Démontrer l'importance du RAD par contraste")
        print("   Configuration : κ=η=1 FIXES (pas de régulation)")
        print("   Attente : Système diverge de l'équilibre θ=1\n")

        # Création de l'économie (tous modules actifs sauf régulation)
        economy = IRISEconomy(
            initial_agents=self.n_agents,
            gold_factor=1.0,
            universal_income_rate=0.02,
            # ═══════════════════════════════════════════════════════════════
            # CONFIGURATION TÉMOIN (modules actifs, régulation désactivée)
            # ═══════════════════════════════════════════════════════════════
            enable_demographics=True,
            enable_catastrophes=False,            # Pas de chocs pour isoler effet
            enable_price_discovery=True,
            enable_dynamic_business=True,
            enable_business_combustion=True,
            enable_chambre_relance=True,
        )

        # FIXATION de κ et η à 1.0 (désactivation régulation)
        economy.rad.kappa = 1.0
        economy.rad.eta = 1.0

        print(f"État initial :")
        print(f"  Population : {len(economy.agents)} agents")
        print(f"  θ initial : {economy.thermometer():.4f}")
        print(f"\n⚠️  RÉGULATION DÉSACTIVÉE :")
        print(f"  κ (kappa) = 1.0 FIXE (pas de modulation liquidité)")
        print(f"  η (eta) = 1.0 FIXE (pas de modulation production)")
        print(f"  Pas de rééquilibrage automatique du thermomètre θ")

        # Simulation SANS régulation (forcer κ=η=1 à chaque step)
        print(f"\nSimulation de {steps} steps ({steps//12} ans) sans régulation...")

        for step in range(steps):
            economy.step(n_transactions=20)

            # FORCE κ=η=1 à chaque step (désactive complètement le RAD)
            economy.rad.kappa = 1.0
            economy.rad.eta = 1.0

            # Affichage périodique
            if step % 120 == 0:  # Tous les 10 ans
                theta = economy.thermometer()
                indicator = economy.indicator()
                print(f"  Année {step//12:3d} : θ={theta:.4f}, I={indicator:.4f}")

        self.results['no_regulation'] = economy.history

        # Analyse de la divergence
        theta_history = np.array(economy.history['thermometer'])
        indicator_history = np.array(economy.history['indicator'])

        theta_mean = np.mean(theta_history)
        theta_std = np.std(theta_history)
        theta_final = economy.thermometer()
        indicator_final = economy.indicator()

        # Calcul de la tendance (drift)
        theta_drift = theta_final - theta_history[0]

        print(f"\n📈 Résultats (no regulation) :")
        print(f"  ═══════════════════════════════════════════════════════════")
        print(f"  DIVERGENCE THERMODYNAMIQUE :")
        print(f"    Thermomètre θ moyen : {theta_mean:.4f} (cible = 1.0)")
        print(f"    Écart-type θ : {theta_std:.4f}")
        print(f"    Thermomètre θ final : {theta_final:.4f}")
        print(f"    Dérive (drift) : {theta_drift:+.4f}")
        print(f"  ═══════════════════════════════════════════════════════════")
        print(f"  ABSENCE DE RÉGULATION :")
        print(f"    Indicateur I final : {indicator_final:.4f} (cible = 0.0)")
        print(f"    Kappa κ : 1.0000 (FIXE)")
        print(f"    Eta η : 1.0000 (FIXE)")
        print(f"  ═══════════════════════════════════════════════════════════")
        print(f"  ÉTAT FINAL :")
        print(f"    Population : {len(economy.agents)} agents")
        print(f"    Gini : {economy.gini_coefficient():.4f}")
        print(f"  ═══════════════════════════════════════════════════════════")

        # Évaluation de la stabilité (normalement mauvaise)
        if abs(theta_final - 1.0) > 0.2:
            print(f"  ❌ SYSTÈME INSTABLE : θ diverge significativement de 1.0")
            print(f"  ➜  Démontre l'importance de la régulation RAD")
        elif abs(theta_final - 1.0) > 0.1:
            print(f"  🟡 SYSTÈME PARTIELLEMENT INSTABLE : Déséquilibre modéré")
        else:
            print(f"  ⚠️  Résultat inattendu : système reste proche de l'équilibre")
            print(f"  ➜  Peut indiquer une durée de simulation trop courte")

        print("\n💡 RECOMMANDATION : Comparer avec run_baseline_stable() pour voir")
        print("   l'effet stabilisateur du RAD (θ oscille autour de 1 vs dérive)")
        print("\n" + "="*70 + "\n")

        return economy

    def run_thermodynamic_underheat(self, steps: int = 600) -> IRISEconomy:
        """
        ÉTAPE 3 - SCÉNARIO THERMODYNAMIQUE 1 : SOUS-CHAUFFE

        État initial : θ < 1 (D/V_on < 1)
        Situation : Sous-régime, économie léthargique, besoin de stimulation

        Attente RAD :
        - κ doit augmenter (> 1) → plus de liquidité injectée
        - η doit augmenter (> 1) → productivité stimulée
        - θ doit converger vers 1.0

        Méthode :
        - Démarrage normal (θ ≈ 1)
        - Choc de destruction de D à t=50 → θ descend brutalement
        - RAD doit détecter sous-chauffe et stimuler

        Args:
            steps: Durée de simulation (50 ans = 600 steps)

        Returns:
            Économie après simulation
        """
        print("\n" + "="*70)
        print("SCÉNARIO THERMODYNAMIQUE 1 : SOUS-CHAUFFE (θ < 1)")
        print("="*70)
        print("État initial : Sous-régime économique (D < V_on)")
        print("Objectif : Vérifier que le RAD stimule (κ ↑, η ↑) et θ → 1")
        print("="*70)

        economy = IRISEconomy(
            initial_agents=self.n_agents,
            enable_demographics=True,
            enable_catastrophes=False,  # Pas de perturbations aléatoires
            enable_business_combustion=True,
            enable_dynamic_business=True,
            enable_chambre_relance=True,
            seed=42  # Reproductibilité
        )

        print(f"\n📊 État initial :")
        print(f"  θ initial : {economy.thermometer():.4f}")
        print(f"  κ initial : {economy.rad.kappa:.4f}")
        print(f"  η initial : {economy.rad.eta:.4f}")

        # Phase 1 : Équilibre initial (50 steps)
        print(f"\n⏳ Phase 1 : Équilibre initial (50 mois)...")
        for _ in range(50):
            economy.step(n_transactions=10)

        print(f"  θ après phase 1 : {economy.thermometer():.4f}")

        # Phase 2 : CHOC DE SOUS-CHAUFFE - Réduction brutale de D
        print(f"\n💥 Phase 2 : CHOC - Destruction de 40% de D (création sous-chauffe)...")
        D_before = economy.rad.total_D()
        economy.rad.D_materielle *= 0.6
        economy.rad.D_contractuelle *= 0.6
        economy.rad.D_services *= 0.6
        D_after = economy.rad.total_D()

        theta_post_shock = economy.thermometer()
        print(f"  D avant choc : {D_before:.2f}")
        print(f"  D après choc : {D_after:.2f} (-40%)")
        print(f"  θ après choc : {theta_post_shock:.4f} << 1.0 (SOUS-CHAUFFE)")

        # Phase 3 : Régulation RAD (550 steps restants)
        print(f"\n⏳ Phase 3 : Régulation RAD ({steps - 50} mois)...")
        print(f"  Attente : κ ↑ et η ↑ pour stimuler l'économie")

        for i in range(steps - 50):
            economy.step(n_transactions=10)

            # Affichage tous les 120 steps (10 ans)
            if (i + 1) % 120 == 0:
                years = (i + 1) // 12
                theta = economy.thermometer()
                kappa = economy.rad.kappa
                eta = economy.rad.eta
                print(f"  +{years} ans : θ={theta:.4f}, κ={kappa:.4f}, η={eta:.4f}")

        # Résultats finaux
        print(f"\n📈 RÉSULTATS FINAUX (SOUS-CHAUFFE) :")
        theta_final = economy.thermometer()
        kappa_final = economy.rad.kappa
        eta_final = economy.rad.eta

        print(f"  θ final : {theta_final:.4f} (cible: 1.0)")
        print(f"  κ final : {kappa_final:.4f} (stimulation: κ > 1.0)")
        print(f"  η final : {eta_final:.4f} (stimulation: η > 1.0)")

        # Validation
        if 0.9 <= theta_final <= 1.1:
            print(f"  ✓ Régulation réussie : θ revenu à l'équilibre")
        else:
            print(f"  ✗ Régulation instable : θ = {theta_final:.4f}")

        if kappa_final > 1.0 or eta_final > 1.0:
            print(f"  ✓ Stimulation active détectée")

        print("="*70 + "\n")

        self.results['underheat'] = economy.history
        return economy

    def run_thermodynamic_normal(self, steps: int = 600) -> IRISEconomy:
        """
        ÉTAPE 3 - SCÉNARIO THERMODYNAMIQUE 2 : NORMAL (ÉQUILIBRE)

        État initial : θ ≈ 1 (D/V_on ≈ 1)
        Situation : Équilibre thermodynamique stable

        Attente RAD :
        - κ oscille autour de 1.0 (pas de correction forte)
        - η oscille autour de 1.0 (production normale)
        - θ reste proche de 1.0 (±10%)

        Méthode :
        - Démarrage normal (θ ≈ 1)
        - Pas de chocs majeurs
        - Petites perturbations naturelles (démographie)
        - RAD doit maintenir l'équilibre

        Args:
            steps: Durée de simulation (50 ans = 600 steps)

        Returns:
            Économie après simulation
        """
        print("\n" + "="*70)
        print("SCÉNARIO THERMODYNAMIQUE 2 : NORMAL (θ ≈ 1)")
        print("="*70)
        print("État initial : Équilibre thermodynamique (D ≈ V_on)")
        print("Objectif : Vérifier que le RAD maintient θ ≈ 1 sans dérive")
        print("="*70)

        economy = IRISEconomy(
            initial_agents=self.n_agents,
            enable_demographics=True,
            enable_catastrophes=False,
            enable_business_combustion=True,
            enable_dynamic_business=True,
            enable_chambre_relance=True,
            seed=42
        )

        print(f"\n📊 État initial :")
        print(f"  θ initial : {economy.thermometer():.4f}")
        print(f"  κ initial : {economy.rad.kappa:.4f}")
        print(f"  η initial : {economy.rad.eta:.4f}")

        print(f"\n⏳ Simulation en cours ({steps // 12} ans = {steps} mois)...")
        print(f"  Aucun choc appliqué - évolution naturelle")

        for i in range(steps):
            economy.step(n_transactions=10)

            # Affichage tous les 120 steps (10 ans)
            if (i + 1) % 120 == 0:
                years = (i + 1) // 12
                theta = economy.thermometer()
                kappa = economy.rad.kappa
                eta = economy.rad.eta
                print(f"  +{years} ans : θ={theta:.4f}, κ={kappa:.4f}, η={eta:.4f}")

        # Résultats finaux
        print(f"\n📈 RÉSULTATS FINAUX (NORMAL) :")
        theta_final = economy.thermometer()
        kappa_final = economy.rad.kappa
        eta_final = economy.rad.eta

        # Calcul de la stabilité de θ
        theta_history = economy.history.get('theta', [])
        if len(theta_history) > 0:
            theta_mean = np.mean(theta_history[-120:])  # Moyenne sur dernier an
            theta_std = np.std(theta_history[-120:])
            print(f"  θ final : {theta_final:.4f} (cible: 1.0)")
            print(f"  θ moyen (dernier an) : {theta_mean:.4f}")
            print(f"  θ écart-type : {theta_std:.4f}")

        print(f"  κ final : {kappa_final:.4f} (équilibre: κ ≈ 1.0)")
        print(f"  η final : {eta_final:.4f} (équilibre: η ≈ 1.0)")

        # Validation
        if 0.8 <= theta_final <= 1.2:
            print(f"  ✓ Équilibre maintenu : θ ∈ [0.8, 1.2]")
        else:
            print(f"  ✗ Dérive détectée : θ = {theta_final:.4f}")

        if 0.8 <= kappa_final <= 1.2 and 0.8 <= eta_final <= 1.2:
            print(f"  ✓ Régulation stable : κ, η proches de 1.0")

        print("="*70 + "\n")

        self.results['normal'] = economy.history
        return economy

    def run_thermodynamic_overheat(self, steps: int = 600) -> IRISEconomy:
        """
        ÉTAPE 3 - SCÉNARIO THERMODYNAMIQUE 3 : SURCHAUFFE

        État initial : θ > 1 (D/V_on > 1)
        Situation : Surchauffe économique, sur-investissement, besoin de freinage

        Attente RAD :
        - κ doit diminuer (< 1) → moins de liquidité injectée
        - η doit diminuer (< 1) → productivité freinée
        - θ doit converger vers 1.0

        Méthode :
        - Démarrage normal (θ ≈ 1)
        - Choc d'injection de D à t=50 → θ monte brutalement
        - RAD doit détecter surchauffe et freiner

        Args:
            steps: Durée de simulation (50 ans = 600 steps)

        Returns:
            Économie après simulation
        """
        print("\n" + "="*70)
        print("SCÉNARIO THERMODYNAMIQUE 3 : SURCHAUFFE (θ > 1)")
        print("="*70)
        print("État initial : Surchauffe économique (D > V_on)")
        print("Objectif : Vérifier que le RAD freine (κ ↓, η ↓) et θ → 1")
        print("="*70)

        economy = IRISEconomy(
            initial_agents=self.n_agents,
            enable_demographics=True,
            enable_catastrophes=False,
            enable_business_combustion=True,
            enable_dynamic_business=True,
            enable_chambre_relance=True,
            seed=42
        )

        print(f"\n📊 État initial :")
        print(f"  θ initial : {economy.thermometer():.4f}")
        print(f"  κ initial : {economy.rad.kappa:.4f}")
        print(f"  η initial : {economy.rad.eta:.4f}")

        # Phase 1 : Équilibre initial (50 steps)
        print(f"\n⏳ Phase 1 : Équilibre initial (50 mois)...")
        for _ in range(50):
            economy.step(n_transactions=10)

        print(f"  θ après phase 1 : {economy.thermometer():.4f}")

        # Phase 2 : CHOC DE SURCHAUFFE - Injection brutale de D
        print(f"\n💥 Phase 2 : CHOC - Injection de +60% de D (création surchauffe)...")
        D_before = economy.rad.total_D()
        economy.rad.D_materielle *= 1.6
        economy.rad.D_contractuelle *= 1.6
        economy.rad.D_services *= 1.6
        D_after = economy.rad.total_D()

        theta_post_shock = economy.thermometer()
        print(f"  D avant choc : {D_before:.2f}")
        print(f"  D après choc : {D_after:.2f} (+60%)")
        print(f"  θ après choc : {theta_post_shock:.4f} >> 1.0 (SURCHAUFFE)")

        # Phase 3 : Régulation RAD (550 steps restants)
        print(f"\n⏳ Phase 3 : Régulation RAD ({steps - 50} mois)...")
        print(f"  Attente : κ ↓ et η ↓ pour freiner l'économie")

        for i in range(steps - 50):
            economy.step(n_transactions=10)

            # Affichage tous les 120 steps (10 ans)
            if (i + 1) % 120 == 0:
                years = (i + 1) // 12
                theta = economy.thermometer()
                kappa = economy.rad.kappa
                eta = economy.rad.eta
                print(f"  +{years} ans : θ={theta:.4f}, κ={kappa:.4f}, η={eta:.4f}")

        # Résultats finaux
        print(f"\n📈 RÉSULTATS FINAUX (SURCHAUFFE) :")
        theta_final = economy.thermometer()
        kappa_final = economy.rad.kappa
        eta_final = economy.rad.eta

        print(f"  θ final : {theta_final:.4f} (cible: 1.0)")
        print(f"  κ final : {kappa_final:.4f} (freinage: κ < 1.0)")
        print(f"  η final : {eta_final:.4f} (freinage: η < 1.0)")

        # Validation
        if 0.9 <= theta_final <= 1.1:
            print(f"  ✓ Régulation réussie : θ revenu à l'équilibre")
        else:
            print(f"  ✗ Régulation instable : θ = {theta_final:.4f}")

        if kappa_final < 1.0 or eta_final < 1.0:
            print(f"  ✓ Freinage actif détecté")

        print("="*70 + "\n")

        self.results['overheat'] = economy.history
        return economy


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
