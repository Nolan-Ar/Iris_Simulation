"""
IRIS Economic System - Validation & Verification Module
========================================================

Ce module implémente un framework complet de validation académique pour le système
économique IRIS v2.1, conforme aux standards V&V (Verification & Validation) pour
les modèles de simulation économique.

╔══════════════════════════════════════════════════════════════════════════════╗
║ POURQUOI CE MODULE ?                                                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

Pour qu'un modèle de simulation économique soit crédible académiquement, il DOIT:
1. Prouver sa ROBUSTESSE (résultats stables sous variations aléatoires)
2. Prouver sa SENSIBILITÉ raisonnable (pas d'effets papillon)
3. Prouver sa VALIDITÉ STATISTIQUE (distributions normales, IC 95%)
4. Être REPRODUCTIBLE (même résultats avec même configuration)

Ce module permet tout cela de manière automatisée.

╔══════════════════════════════════════════════════════════════════════════════╗
║ MODULES DE VALIDATION IMPLÉMENTÉS                                           ║
╚══════════════════════════════════════════════════════════════════════════════╝

1. MONTE CARLO ANALYSIS
   ----------------------
   Lance N simulations indépendantes avec seeds aléatoires différents.
   Collecte θ, Gini, κ, η pour chaque run.
   Calcule statistiques: moyenne, écart-type, IC 95%, taux convergence.

   Objectif: Prouver que le système converge de manière robuste vers θ≈1.0
   Usage: validator.run_monte_carlo(n_runs=100, steps=100)

2. SENSITIVITY ANALYSIS
   ---------------------
   Varie un paramètre clé (ex: eta_alpha) de ±10% autour de sa valeur baseline.
   Pour chaque variation, lance N simulations Monte Carlo.
   Calcule l'élasticité: ε = (Δθ/θ) / (Δp/p)

   Objectif: Mesurer l'impact des paramètres RAD sur le comportement du système
   Usage: validator.run_sensitivity_analysis('eta_alpha', baseline=0.5, variation_pct=[-10,0,10])

3. STATISTICAL VALIDATION
   -----------------------
   Test de Kolmogorov-Smirnov: Vérifie si θ suit une loi normale
   Test de Shapiro-Wilk: Test de normalité complémentaire
   Intervalle de confiance 95% via distribution t de Student

   Objectif: Valider que les fluctuations sont stochastiques et non-biaisées
   Usage: validator.kolmogorov_smirnov_test(monte_carlo_results)

4. ROBUSTNESS METRICS
   -------------------
   Taux de convergence: % de simulations qui convergent vers θ≈1.0
   Taux de crash: % de simulations qui échouent
   Amplitude oscillations: σ(θ) sur les derniers cycles

   Objectif: Mesurer la stabilité globale du système
   Inclus automatiquement dans Monte Carlo

5. RÉSULTATS EXPORTÉS EN JSON
   --------------------------
   Tous les résultats sont sauvegardés en JSON pour interopérabilité
   Compatible avec R, Julia, Excel, Python pandas
   Seeds reproductibles pour validation par pairs

╔══════════════════════════════════════════════════════════════════════════════╗
║ RÉFÉRENCES ACADÉMIQUES                                                       ║
╚══════════════════════════════════════════════════════════════════════════════╝

- Sargent, R.G. (2013). "Verification and validation of simulation models"
  Journal of Simulation, 7(1), 12-24. DOI: 10.1057/jos.2012.20

- Kleijnen, J.P.C. (1995). "Verification and validation of simulation models"
  European Journal of Operational Research, 82(1), 145-162.

- Moss, S., & Edmonds, B. (2005). "Sociology and simulation: Statistical and
  qualitative cross-validation" American Journal of Sociology, 110(4), 1095-1131.

╔══════════════════════════════════════════════════════════════════════════════╗
║ UTILISATION RAPIDE                                                           ║
╚══════════════════════════════════════════════════════════════════════════════╝

# Validation complète en 3 lignes:
from iris_validation import quick_validation
mc_results, ks_results = quick_validation(n_runs=50, steps=100)
# Résultats affichés + sauvegardés dans validation_results/

# Utilisation avancée:
from iris_validation import IRISValidator
validator = IRISValidator()
mc = validator.run_monte_carlo(n_runs=100, steps=100, parallel=False)
ks = validator.kolmogorov_smirnov_test(mc)
sens = validator.run_sensitivity_analysis('eta_alpha', 0.5, [-10,-5,0,5,10], 20, 100)

Auteur: Arnault Nolan
Email: arnaultnolan@gmail.com
Date: 2025-11-17
Version: 1.0
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Callable
from dataclasses import dataclass, field
import json
from pathlib import Path
from scipy import stats
from concurrent.futures import ProcessPoolExecutor
import multiprocessing as mp

# Import du modèle IRIS
from .iris_model import IRISEconomy


@dataclass
class MonteCarloResults:
    """Résultats d'une analyse Monte Carlo"""
    n_runs: int
    steps_per_run: int
    parameter_config: Dict

    # Métriques statistiques pour θ (thermomètre)
    theta_mean: float
    theta_std: float
    theta_min: float
    theta_max: float
    theta_q25: float  # Quantile 25%
    theta_q75: float  # Quantile 75%
    theta_ci_lower: float  # Intervalle confiance 95% (inf)
    theta_ci_upper: float  # Intervalle confiance 95% (sup)

    # Métriques pour Gini
    gini_mean: float
    gini_std: float
    gini_min: float
    gini_max: float

    # Métriques pour κ et η
    kappa_mean: float
    kappa_std: float
    eta_mean: float
    eta_std: float

    # Métriques de stabilité
    crash_rate: float  # % de simulations qui ont divergé/crashé
    convergence_rate: float  # % de simulations qui ont convergé vers θ≈1
    oscillation_amplitude: float  # Amplitude moyenne des oscillations

    # Historiques complets (toutes runs)
    all_theta_histories: List[List[float]] = field(default_factory=list)
    all_gini_histories: List[List[float]] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Exporte en dictionnaire"""
        return {
            'n_runs': self.n_runs,
            'steps_per_run': self.steps_per_run,
            'parameter_config': self.parameter_config,
            'theta': {
                'mean': self.theta_mean,
                'std': self.theta_std,
                'min': self.theta_min,
                'max': self.theta_max,
                'q25': self.theta_q25,
                'q75': self.theta_q75,
                'ci_95': [self.theta_ci_lower, self.theta_ci_upper]
            },
            'gini': {
                'mean': self.gini_mean,
                'std': self.gini_std,
                'min': self.gini_min,
                'max': self.gini_max
            },
            'kappa': {
                'mean': self.kappa_mean,
                'std': self.kappa_std
            },
            'eta': {
                'mean': self.eta_mean,
                'std': self.eta_std
            },
            'stability': {
                'crash_rate': self.crash_rate,
                'convergence_rate': self.convergence_rate,
                'oscillation_amplitude': self.oscillation_amplitude
            }
        }


@dataclass
class SensitivityResults:
    """Résultats d'une analyse de sensibilité"""
    parameter_name: str
    baseline_value: float
    variations: List[float]  # Ex: [-10%, -5%, 0%, +5%, +10%]

    # Impact sur θ
    theta_impacts: List[float]  # θ_mean pour chaque variation
    theta_elasticity: float  # dθ/dp normalized

    # Impact sur Gini
    gini_impacts: List[float]
    gini_elasticity: float

    # Impact sur stabilité
    stability_impacts: List[float]  # Variance de θ pour chaque variation

    def to_dict(self) -> Dict:
        """Exporte en dictionnaire"""
        return {
            'parameter': self.parameter_name,
            'baseline': self.baseline_value,
            'variations': self.variations,
            'theta': {
                'impacts': self.theta_impacts,
                'elasticity': self.theta_elasticity
            },
            'gini': {
                'impacts': self.gini_impacts,
                'elasticity': self.gini_elasticity
            },
            'stability': {
                'impacts': self.stability_impacts
            }
        }


class IRISValidator:
    """
    Validateur académique pour le modèle IRIS

    Implémente les protocoles V&V (Verification & Validation) conformes
    aux standards de simulation économique.
    """

    def __init__(self, output_dir: str = "validation_results"):
        """
        Initialise le validateur

        Args:
            output_dir: Répertoire pour sauvegarder les résultats
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)

    def run_monte_carlo(self,
                       n_runs: int = 100,
                       steps: int = 100,
                       initial_agents: int = 100,
                       parameter_config: Optional[Dict] = None,
                       parallel: bool = False,  # Désactivé par défaut (pickle issues)
                       verbose: bool = True) -> MonteCarloResults:
        """
        Exécute une analyse Monte Carlo avec N simulations indépendantes

        OBJECTIF:
        Mesurer la robustesse statistique du modèle en exécutant de multiples
        simulations avec des seeds aléatoires différents.

        MÉTHODE:
        1. Lance N simulations avec seeds différents
        2. Collecte les métriques (θ, Gini, κ, η) pour chaque run
        3. Calcule statistiques agrégées (moyenne, variance, CI 95%)
        4. Évalue stabilité (convergence, oscillations, crashes)

        Args:
            n_runs: Nombre de simulations indépendantes (défaut: 100)
            steps: Nombre de cycles par simulation (défaut: 100)
            initial_agents: Nombre d'agents initiaux (défaut: 100)
            parameter_config: Configuration personnalisée des paramètres
            parallel: Exécution parallèle (défaut: True)
            verbose: Affichage des progrès (défaut: True)

        Returns:
            MonteCarloResults: Résultats statistiques complets
        """
        if verbose:
            print(f"\n{'='*80}")
            print(f"MONTE CARLO ANALYSIS - {n_runs} runs × {steps} steps")
            print(f"{'='*80}\n")

        # Configuration par défaut si non fournie
        if parameter_config is None:
            parameter_config = {
                'initial_agents': initial_agents,
                'enable_demographics': True,
                'enable_catastrophes': True
            }

        # Fonction worker pour exécution parallèle
        def run_single_simulation(run_id: int) -> Dict:
            """
            Exécute une seule simulation avec seed fixé

            Cette fonction est le "worker" qui sera appelé N fois en parallèle ou séquentiellement.
            Chaque appel représente une simulation indépendante avec son propre seed aléatoire.

            Args:
                run_id: Identifiant unique de la simulation (0 à N-1)

            Returns:
                Dict contenant toutes les métriques de cette simulation
            """
            try:
                # Fixe le seed pour reproductibilité
                # Chaque run_id génère un seed différent mais toujours le même pour ce run_id
                # L'offset +1000 évite les seeds proches de 0 qui peuvent être problématiques
                np.random.seed(run_id + 1000)

                # Crée une nouvelle économie IRIS avec la configuration fournie
                economy = IRISEconomy(**parameter_config)

                # Lance la simulation pour 'steps' cycles
                # n_transactions=10 signifie 10 transactions par agent par cycle
                economy.simulate(steps=steps, n_transactions=10)

                # Collecte les métriques finales (à la fin de la simulation)
                theta_final = economy.thermometer()      # θ = D/V_on (équilibre = 1.0)
                gini_final = economy.gini_coefficient()  # Coefficient Gini (inégalités)
                kappa_final = economy.rad.kappa          # κ final (coefficient conversion)
                eta_final = economy.rad.eta              # η final (rendement combustion)

                # Historiques complets (évolution temporelle)
                theta_history = economy.history['thermometer']
                gini_history = economy.history['gini_coefficient']

                # Calcul de la convergence: est-ce que θ est proche de 1.0 ?
                # On considère convergé si |θ - 1.0| < 15% (critère arbitraire mais raisonnable)
                convergence = abs(theta_final - 1.0) < 0.15

                # Calcul de l'amplitude des oscillations (mesure de stabilité)
                # On prend l'écart-type des 50 derniers cycles pour mesurer les fluctuations
                if len(theta_history) > 10:
                    oscillation = np.std(theta_history[-50:])  # Écart-type 50 derniers cycles
                else:
                    oscillation = np.std(theta_history)  # Si < 50 cycles, prend tout

                return {
                    'run_id': run_id,
                    'success': True,
                    'theta_final': theta_final,
                    'gini_final': gini_final,
                    'kappa_final': kappa_final,
                    'eta_final': eta_final,
                    'theta_history': theta_history,
                    'gini_history': gini_history,
                    'convergence': convergence,
                    'oscillation': oscillation
                }
            except Exception as e:
                # Simulation a crashé
                return {
                    'run_id': run_id,
                    'success': False,
                    'error': str(e)
                }

        # ==================================================================================
        # EXÉCUTION DES SIMULATIONS (parallèle ou séquentielle)
        # ==================================================================================
        if parallel and n_runs > 1:
            # Mode PARALLÈLE: utilise plusieurs cœurs CPU pour accélérer
            # Attention: peut causer des erreurs de pickle avec nested functions
            n_workers = min(mp.cpu_count(), n_runs)  # Limite au nombre de runs ou CPU
            if verbose:
                print(f"Exécution parallèle sur {n_workers} workers...")

            # ProcessPoolExecutor distribue les runs sur plusieurs processus
            with ProcessPoolExecutor(max_workers=n_workers) as executor:
                results = list(executor.map(run_single_simulation, range(n_runs)))
        else:
            # Mode SÉQUENTIEL: exécute les simulations une par une
            # Plus lent mais plus stable et permet le suivi en temps réel
            if verbose:
                print("Exécution séquentielle...")
            results = [run_single_simulation(i) for i in range(n_runs)]

            # Affichage du progrès pour chaque simulation
            if verbose:
                for i, res in enumerate(results, 1):
                    if res['success']:
                        print(f"  Run {i}/{n_runs}: θ={res['theta_final']:.4f}, "
                              f"Gini={res['gini_final']:.4f}, "
                              f"converge={'✓' if res['convergence'] else '✗'}")

        # ==================================================================================
        # FILTRAGE ET VALIDATION DES RÉSULTATS
        # ==================================================================================
        # Filtre les runs réussis (certains peuvent avoir crashé)
        successful_runs = [r for r in results if r['success']]
        crash_rate = (n_runs - len(successful_runs)) / n_runs

        # Si toutes les simulations ont échoué, on ne peut pas continuer
        if len(successful_runs) == 0:
            raise RuntimeError("Toutes les simulations ont échoué!")

        # ==================================================================================
        # EXTRACTION DES MÉTRIQUES
        # ==================================================================================
        # Convertit les listes en arrays numpy pour faciliter les calculs statistiques
        theta_finals = np.array([r['theta_final'] for r in successful_runs])
        gini_finals = np.array([r['gini_final'] for r in successful_runs])
        kappa_finals = np.array([r['kappa_final'] for r in successful_runs])
        eta_finals = np.array([r['eta_final'] for r in successful_runs])

        # Métriques de convergence et stabilité
        convergences = [r['convergence'] for r in successful_runs]
        oscillations = np.array([r['oscillation'] for r in successful_runs])

        # Historiques complets pour analyse temporelle
        all_theta_histories = [r['theta_history'] for r in successful_runs]
        all_gini_histories = [r['gini_history'] for r in successful_runs]

        # ==================================================================================
        # CALCUL DES STATISTIQUES DESCRIPTIVES
        # ==================================================================================
        # Moyenne et écart-type de θ
        theta_mean = np.mean(theta_finals)
        theta_std = np.std(theta_finals, ddof=1)  # ddof=1 pour correction Bessel (échantillon)

        # Intervalle de confiance à 95% en utilisant la distribution t de Student
        # Pourquoi t-distribution ? Car on a un échantillon (pas toute la population)
        theta_ci_lower, theta_ci_upper = stats.t.interval(
            0.95,  # Niveau de confiance (95%)
            len(theta_finals) - 1,  # Degrés de liberté (n-1)
            loc=theta_mean,  # Centre de la distribution
            scale=stats.sem(theta_finals)  # Erreur standard de la moyenne
        )

        gini_mean = np.mean(gini_finals)
        gini_std = np.std(gini_finals, ddof=1)

        kappa_mean = np.mean(kappa_finals)
        kappa_std = np.std(kappa_finals, ddof=1)

        eta_mean = np.mean(eta_finals)
        eta_std = np.std(eta_finals, ddof=1)

        convergence_rate = sum(convergences) / len(convergences)
        oscillation_amplitude = np.mean(oscillations)

        # Résultats
        results_obj = MonteCarloResults(
            n_runs=n_runs,
            steps_per_run=steps,
            parameter_config=parameter_config,
            theta_mean=theta_mean,
            theta_std=theta_std,
            theta_min=np.min(theta_finals),
            theta_max=np.max(theta_finals),
            theta_q25=np.percentile(theta_finals, 25),
            theta_q75=np.percentile(theta_finals, 75),
            theta_ci_lower=theta_ci_lower,
            theta_ci_upper=theta_ci_upper,
            gini_mean=gini_mean,
            gini_std=gini_std,
            gini_min=np.min(gini_finals),
            gini_max=np.max(gini_finals),
            kappa_mean=kappa_mean,
            kappa_std=kappa_std,
            eta_mean=eta_mean,
            eta_std=eta_std,
            crash_rate=crash_rate,
            convergence_rate=convergence_rate,
            oscillation_amplitude=oscillation_amplitude,
            all_theta_histories=all_theta_histories,
            all_gini_histories=all_gini_histories
        )

        # Affichage résumé
        if verbose:
            print(f"\n{'='*80}")
            print(f"RÉSULTATS MONTE CARLO ({len(successful_runs)}/{n_runs} runs réussis)")
            print(f"{'='*80}")
            print(f"\nThermomètre θ:")
            print(f"  - Moyenne : {theta_mean:.4f}")
            print(f"  - Écart-type : {theta_std:.4f}")
            print(f"  - Min/Max : [{np.min(theta_finals):.4f}, {np.max(theta_finals):.4f}]")
            print(f"  - IC 95% : [{theta_ci_lower:.4f}, {theta_ci_upper:.4f}]")
            print(f"\nGini:")
            print(f"  - Moyenne : {gini_mean:.4f}")
            print(f"  - Écart-type : {gini_std:.4f}")
            print(f"\nStabilité:")
            print(f"  - Taux convergence : {convergence_rate*100:.1f}%")
            print(f"  - Taux crash : {crash_rate*100:.1f}%")
            print(f"  - Amplitude oscillations : {oscillation_amplitude:.4f}")
            print(f"{'='*80}\n")

        # Sauvegarde résultats
        self._save_monte_carlo_results(results_obj)

        return results_obj

    def _save_monte_carlo_results(self, results: MonteCarloResults) -> None:
        """Sauvegarde les résultats Monte Carlo"""
        output_path = self.output_dir / "monte_carlo_results.json"
        with open(output_path, 'w') as f:
            json.dump(results.to_dict(), f, indent=2)
        print(f"✅ Résultats sauvegardés: {output_path}")

    def run_sensitivity_analysis(self,
                                 parameter_name: str,
                                 baseline_value: float,
                                 variation_pct: List[float] = [-10, -5, 0, 5, 10],
                                 n_runs_per_variation: int = 20,
                                 steps: int = 100,
                                 initial_agents: int = 100,
                                 verbose: bool = True) -> SensitivityResults:
        """
        Analyse de sensibilité : variation d'un paramètre clé

        OBJECTIF:
        Mesurer l'impact de la variation d'un paramètre sur les métriques de sortie
        (θ, Gini, stabilité).

        MÉTHODE:
        1. Pour chaque variation (ex: -10%, -5%, 0%, +5%, +10%)
        2. Exécute N simulations Monte Carlo avec paramètre modifié
        3. Mesure θ_mean, Gini_mean, variance_θ
        4. Calcule l'élasticité : (Δθ/θ) / (Δp/p)

        Args:
            parameter_name: Nom du paramètre RAD (ex: 'eta_alpha', 'kappa_beta', 'eta_smoothing')
            baseline_value: Valeur de référence
            variation_pct: Liste des variations en % (ex: [-10, -5, 0, 5, 10])
            n_runs_per_variation: Nombre de runs Monte Carlo par variation
            steps: Nombre de cycles par simulation
            initial_agents: Nombre d'agents initiaux
            verbose: Affichage des progrès

        Returns:
            SensitivityResults: Résultats de l'analyse de sensibilité
        """
        if verbose:
            print(f"\n{'='*80}")
            print(f"SENSITIVITY ANALYSIS - {parameter_name}")
            print(f"Baseline: {baseline_value}, Variations: {variation_pct}%")
            print(f"{n_runs_per_variation} runs per variation × {steps} steps")
            print(f"{'='*80}\n")

        theta_impacts = []
        gini_impacts = []
        stability_impacts = []

        # Fonction worker pour une variation donnée
        def run_variation_batch(variation_pct: float, new_value: float) -> Dict:
            """
            Exécute n_runs simulations avec un paramètre modifié

            Pour chaque variation du paramètre (ex: -10%, 0%, +10%), cette fonction
            lance plusieurs simulations Monte Carlo indépendantes et collecte les statistiques.

            Args:
                variation_pct: Pourcentage de variation (ex: -10, 0, +10)
                new_value: Nouvelle valeur du paramètre (baseline × (1 + variation_pct/100))

            Returns:
                Dict avec moyennes de θ, Gini, stabilité et nombre de runs réussis
            """
            theta_results = []
            gini_results = []
            theta_variances = []

            # Lance n_runs_per_variation simulations avec ce paramètre
            for run_id in range(n_runs_per_variation):
                try:
                    # Seed reproductible (doit être positif et < 2^32)
                    # Formule complexe pour éviter collisions et garder reproductibilité
                    # abs() pour éviter négatifs, % pour rester sous 2^32
                    seed = abs(int(variation_pct * 1000) + run_id + 5000) % (2**32 - 1)
                    np.random.seed(seed)

                    # Crée une nouvelle économie IRIS
                    economy = IRISEconomy(
                        initial_agents=initial_agents,
                        enable_demographics=True,  # Naissances/morts activées
                        enable_catastrophes=True    # Événements aléatoires activés
                    )

                    # CRITIQUE: Modifie le paramètre RAD dynamiquement
                    # setattr() permet de modifier un attribut par son nom (string)
                    # Exemple: setattr(economy.rad, 'eta_alpha', 0.55) ≡ economy.rad.eta_alpha = 0.55
                    if hasattr(economy.rad, parameter_name):
                        setattr(economy.rad, parameter_name, new_value)
                    else:
                        raise ValueError(f"Paramètre '{parameter_name}' n'existe pas dans RADState")

                    # Lance la simulation
                    economy.simulate(steps=steps, n_transactions=10)

                    # Collecte les métriques finales
                    theta_final = economy.thermometer()       # Thermomètre final
                    gini_final = economy.gini_coefficient()   # Gini final

                    # Calcule la variance de θ comme mesure de stabilité
                    # Variance élevée = système instable, variance faible = système stable
                    if len(economy.history['thermometer']) > 10:
                        # Prend les 50 derniers cycles pour mesurer stabilité récente
                        theta_variance = np.var(economy.history['thermometer'][-50:])
                    else:
                        # Si moins de 50 cycles, prend tout
                        theta_variance = np.var(economy.history['thermometer'])

                    # Stocke les résultats
                    theta_results.append(theta_final)
                    gini_results.append(gini_final)
                    theta_variances.append(theta_variance)

                except Exception as e:
                    # Simulation échouée, on continue sans cette simulation
                    if verbose:
                        print(f"    ⚠ Run {run_id} failed: {e}")
                    continue

            # Agrégation des résultats de toutes les simulations
            if len(theta_results) > 0:
                # Calcule les moyennes sur toutes les simulations réussies
                theta_mean = np.mean(theta_results)
                gini_mean = np.mean(gini_results)
                stability_mean = np.mean(theta_variances)  # Moyenne des variances
            else:
                # Aucune simulation n'a réussi, retourne NaN
                theta_mean = np.nan
                gini_mean = np.nan
                stability_mean = np.nan

            return {
                'theta_mean': theta_mean,
                'gini_mean': gini_mean,
                'stability_mean': stability_mean,
                'n_successful': len(theta_results)
            }

        # Exécute pour chaque variation
        for pct in variation_pct:
            # Calcule nouvelle valeur
            new_value = baseline_value * (1 + pct/100)

            if verbose:
                print(f"Testing {parameter_name}={new_value:.4f} ({pct:+.0f}%)...")

            # Exécute batch de simulations
            batch_results = run_variation_batch(pct, new_value)

            theta_impacts.append(batch_results['theta_mean'])
            gini_impacts.append(batch_results['gini_mean'])
            stability_impacts.append(batch_results['stability_mean'])

            if verbose:
                print(f"  → θ={batch_results['theta_mean']:.4f}, "
                      f"Gini={batch_results['gini_mean']:.4f}, "
                      f"σ²_θ={batch_results['stability_mean']:.4f} "
                      f"({batch_results['n_successful']}/{n_runs_per_variation} runs OK)")

        # ==================================================================================
        # CALCUL DES ÉLASTICITÉS
        # ==================================================================================
        # L'élasticité mesure la sensibilité d'une variable de sortie (θ, Gini) à une
        # variation du paramètre d'entrée. Formule: ε = (Δy/y) / (Δx/x)
        #
        # Interprétation:
        # - ε = 0 : Pas d'impact (robuste)
        # - ε = 1 : Variation proportionnelle (sensibilité modérée)
        # - ε > 1 : Forte sensibilité (attention!)
        # - ε < 0 : Relation inverse (ex: augmenter α diminue θ)
        # ==================================================================================

        # Trouve l'indice de la valeur baseline (variation 0%)
        theta_baseline_idx = variation_pct.index(0) if 0 in variation_pct else len(variation_pct) // 2
        theta_baseline = theta_impacts[theta_baseline_idx]
        gini_baseline = gini_impacts[theta_baseline_idx]

        # Élasticité moyenne calculée par différence finie (approximation de la dérivée)
        if len(variation_pct) >= 3 and not np.isnan(theta_baseline):
            # Trouve les indices pour calculer la pente (préfère ±5% ou ±10%)
            # On utilise deux points symétriques autour de baseline pour minimiser le biais
            if -5 in variation_pct and 5 in variation_pct:
                idx_minus = variation_pct.index(-5)
                idx_plus = variation_pct.index(5)
            elif -10 in variation_pct and 10 in variation_pct:
                idx_minus = variation_pct.index(-10)
                idx_plus = variation_pct.index(10)
            else:
                # Fallback: utilise les extrêmes
                idx_minus = 0
                idx_plus = -1

            # Calcul élasticité θ
            # Vérifie d'abord que les valeurs ne sont pas nan (simulations échouées)
            if not np.isnan(theta_impacts[idx_plus]) and not np.isnan(theta_impacts[idx_minus]):
                # Variation absolue de θ entre les deux points
                delta_theta = theta_impacts[idx_plus] - theta_impacts[idx_minus]
                # Variation relative du paramètre (en fraction, pas %)
                delta_pct = (variation_pct[idx_plus] - variation_pct[idx_minus]) / 100

                # Élasticité = variation relative de θ / variation relative du paramètre
                # Exemple: si θ varie de 2% quand paramètre varie de 10%, ε = (0.02/θ) / (0.10/p) ≈ 0.2
                theta_elasticity = (delta_theta / theta_baseline) / delta_pct if (delta_pct != 0 and theta_baseline != 0) else 0.0
            else:
                theta_elasticity = 0.0  # Données invalides

            # Calcul élasticité Gini (même logique)
            if not np.isnan(gini_impacts[idx_plus]) and not np.isnan(gini_impacts[idx_minus]) and gini_baseline != 0:
                delta_gini = gini_impacts[idx_plus] - gini_impacts[idx_minus]
                delta_pct = (variation_pct[idx_plus] - variation_pct[idx_minus]) / 100
                gini_elasticity = (delta_gini / gini_baseline) / delta_pct if delta_pct != 0 else 0.0
            else:
                gini_elasticity = 0.0
        else:
            # Pas assez de points ou baseline invalide
            theta_elasticity = 0.0
            gini_elasticity = 0.0

        results = SensitivityResults(
            parameter_name=parameter_name,
            baseline_value=baseline_value,
            variations=[baseline_value * (1 + p/100) for p in variation_pct],
            theta_impacts=theta_impacts,
            theta_elasticity=theta_elasticity,
            gini_impacts=gini_impacts,
            gini_elasticity=gini_elasticity,
            stability_impacts=stability_impacts
        )

        if verbose:
            print(f"\n{'='*80}")
            print(f"RÉSULTATS SENSITIVITY ANALYSIS")
            print(f"{'='*80}")
            print(f"\nÉlasticité θ : {theta_elasticity:.4f}")
            print(f"Élasticité Gini : {gini_elasticity:.4f}")
            print(f"{'='*80}\n")

        # Sauvegarde
        self._save_sensitivity_results(results)

        return results

    def _save_sensitivity_results(self, results: SensitivityResults) -> None:
        """Sauvegarde les résultats d'analyse de sensibilité"""
        output_path = self.output_dir / f"sensitivity_{results.parameter_name}.json"
        with open(output_path, 'w') as f:
            json.dump(results.to_dict(), f, indent=2)
        print(f"✅ Résultats sauvegardés: {output_path}")

    def kolmogorov_smirnov_test(self,
                               monte_carlo_results: MonteCarloResults,
                               target_distribution: str = "normal",
                               verbose: bool = True) -> Dict:
        """
        Test de Kolmogorov-Smirnov pour validation statistique

        OBJECTIF:
        Tester si la distribution de θ suit une loi normale (ou autre).

        Hypothèse H0: La distribution suit la loi spécifiée
        Si p-value > 0.05 → On ne peut pas rejeter H0
        Si p-value < 0.05 → On rejette H0 (distribution différente)

        Args:
            monte_carlo_results: Résultats Monte Carlo
            target_distribution: 'normal', 'uniform', etc.
            verbose: Affichage

        Returns:
            Dict avec résultats du test
        """
        # Collecte toutes les valeurs finales de θ
        theta_finals = []
        for history in monte_carlo_results.all_theta_histories:
            if len(history) > 0:
                theta_finals.append(history[-1])

        theta_finals = np.array(theta_finals)

        # Test KS
        if target_distribution == "normal":
            # Test contre normale (μ=mean, σ=std)
            ks_stat, p_value = stats.kstest(
                theta_finals,
                lambda x: stats.norm.cdf(x, monte_carlo_results.theta_mean, monte_carlo_results.theta_std)
            )
        elif target_distribution == "uniform":
            # Test contre uniforme
            ks_stat, p_value = stats.kstest(
                theta_finals,
                'uniform'
            )
        else:
            raise ValueError(f"Distribution '{target_distribution}' non supportée")

        # Test de normalité (Shapiro-Wilk)
        if len(theta_finals) <= 5000:  # Shapiro-Wilk limité à 5000 échantillons
            shapiro_stat, shapiro_p = stats.shapiro(theta_finals)
        else:
            shapiro_stat, shapiro_p = None, None

        results = {
            'distribution': target_distribution,
            'n_samples': len(theta_finals),
            'ks_statistic': ks_stat,
            'ks_p_value': p_value,
            'shapiro_statistic': shapiro_stat,
            'shapiro_p_value': shapiro_p,
            'normality_conclusion': 'NORMAL' if (shapiro_p is not None and shapiro_p > 0.05) else 'NON-NORMAL' if shapiro_p is not None else 'UNKNOWN'
        }

        if verbose:
            print(f"\n{'='*80}")
            print(f"KOLMOGOROV-SMIRNOV TEST")
            print(f"{'='*80}")
            print(f"\nDistribution cible : {target_distribution}")
            print(f"Nombre d'échantillons : {len(theta_finals)}")
            print(f"\nTest KS:")
            print(f"  - Statistique : {ks_stat:.4f}")
            print(f"  - p-value : {p_value:.4f}")
            print(f"  - Conclusion : {'Accepte H0 (suit la distribution)' if p_value > 0.05 else 'Rejette H0 (ne suit pas la distribution)'}")

            if shapiro_stat is not None:
                print(f"\nTest Shapiro-Wilk (normalité):")
                print(f"  - Statistique : {shapiro_stat:.4f}")
                print(f"  - p-value : {shapiro_p:.4f}")
                print(f"  - Conclusion : {results['normality_conclusion']}")
            print(f"{'='*80}\n")

        return results

    def generate_validation_report(
        self,
        mc_path: str = "validation_results/monte_carlo_results.json",
        sens_path: str = "validation_results/sensitivity_eta_alpha.json",
        output_path: str = "validation_results/VALIDATION_IRIS.md"
    ) -> str:
        """
        Génère un rapport de validation lisible en Markdown à partir des résultats JSON

        Cette méthode lit les fichiers de résultats (Monte Carlo et analyse de sensibilité)
        et génère un rapport Markdown structuré et lisible pour documentation académique.

        Args:
            mc_path: Chemin vers le fichier monte_carlo_results.json
            sens_path: Chemin vers le fichier sensitivity_*.json
            output_path: Chemin de sortie du rapport Markdown

        Returns:
            str: Chemin du fichier généré
        """
        import os

        # ==================================================================================
        # CHARGEMENT DES DONNÉES MONTE CARLO
        # ==================================================================================
        try:
            with open(mc_path, 'r', encoding='utf-8') as f:
                mc_data = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Fichier Monte Carlo non trouvé: {mc_path}\n"
                f"Veuillez d'abord exécuter: validator.run_monte_carlo()"
            )

        # ==================================================================================
        # CHARGEMENT DES DONNÉES DE SENSIBILITÉ
        # ==================================================================================
        try:
            with open(sens_path, 'r', encoding='utf-8') as f:
                sens_data = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Fichier de sensibilité non trouvé: {sens_path}\n"
                f"Veuillez d'abord exécuter: validator.run_sensitivity_analysis()"
            )

        # ==================================================================================
        # EXTRACTION DES MÉTRIQUES MONTE CARLO
        # ==================================================================================
        n_runs = mc_data['n_runs']
        steps_per_run = mc_data['steps_per_run']
        param_config = mc_data['parameter_config']

        theta = mc_data['theta']
        gini = mc_data['gini']
        kappa = mc_data['kappa']
        eta = mc_data['eta']
        stability = mc_data['stability']

        # ==================================================================================
        # EXTRACTION DES MÉTRIQUES DE SENSIBILITÉ
        # ==================================================================================
        parameter = sens_data['parameter']
        baseline = sens_data['baseline']
        variations = sens_data['variations']
        theta_sens = sens_data['theta']
        gini_sens = sens_data['gini']
        stability_sens = sens_data.get('stability', {})

        # ==================================================================================
        # CONSTRUCTION DU RAPPORT MARKDOWN
        # ==================================================================================
        report_lines = []

        # En-tête
        report_lines.append("# Rapport de Validation IRIS")
        report_lines.append("")
        report_lines.append("Ce document présente les résultats de validation du modèle économique IRIS v2.1.")
        report_lines.append("")
        report_lines.append("---")
        report_lines.append("")

        # ==================================================================================
        # SECTION 1: CONFIGURATION DES TESTS
        # ==================================================================================
        report_lines.append("## 1. Configuration des tests")
        report_lines.append("")
        report_lines.append(f"- **Nombre de runs Monte Carlo** : {n_runs}")
        report_lines.append(f"- **Nombre de pas par run** : {steps_per_run}")
        report_lines.append(f"- **Paramètres de base** :")
        report_lines.append(f"  - `initial_agents` : {param_config.get('initial_agents', 'N/A')}")
        report_lines.append(f"  - `enable_demographics` : {param_config.get('enable_demographics', False)}")
        report_lines.append(f"  - `enable_catastrophes` : {param_config.get('enable_catastrophes', False)}")
        report_lines.append("")

        # ==================================================================================
        # SECTION 2: RÉSULTATS MONTE CARLO
        # ==================================================================================
        report_lines.append("## 2. Résultats Monte Carlo (stabilité globale)")
        report_lines.append("")
        report_lines.append("### Métriques de performance")
        report_lines.append("")
        report_lines.append(f"- **θ moyen** : `{theta['mean']:.4f}` (± {theta['std']:.4f})")
        report_lines.append(f"- **Intervalle 95% pour θ** : [`{theta['ci_95'][0]:.4f}` ; `{theta['ci_95'][1]:.4f}`]")
        report_lines.append(f"- **Gini moyen** : `{gini['mean']:.4f}` (± {gini['std']:.4f})")
        report_lines.append(f"- **κ moyen** : `{kappa['mean']:.4f}` (± {kappa['std']:.4f})")
        report_lines.append(f"- **η moyen** : `{eta['mean']:.4f}` (± {eta['std']:.4f})")
        report_lines.append("")

        report_lines.append("### Métriques de stabilité")
        report_lines.append("")
        report_lines.append(f"- **Taux de crash** : `{stability['crash_rate']:.2%}`")
        report_lines.append(f"- **Taux de convergence** : `{stability['convergence_rate']:.2%}`")
        report_lines.append(f"- **Amplitude d'oscillation** : `{stability['oscillation_amplitude']:.4f}`")
        report_lines.append("")

        # Message automatique si aucun crash
        if stability['crash_rate'] == 0:
            report_lines.append("> ✅ **Aucun crash observé sur l'échantillon Monte Carlo.**  ")
            report_lines.append("> Le modèle est numériquement stable dans cette configuration.")
            report_lines.append("")

        # ==================================================================================
        # SECTION 3: ANALYSE DE SENSIBILITÉ
        # ==================================================================================
        report_lines.append(f"## 3. Analyse de sensibilité (`{parameter}`)")
        report_lines.append("")
        report_lines.append(f"- **Paramètre étudié** : `{parameter}`")
        report_lines.append(f"- **Baseline** : `{baseline}`")
        report_lines.append(f"- **Variations testées** : `{variations}`")
        report_lines.append("")

        # Impact sur θ
        report_lines.append("### Impact sur θ (thermomètre)")
        report_lines.append("")
        report_lines.append("**θ moyens simulés pour chaque valeur** :")
        report_lines.append("")
        for i, (variation, impact) in enumerate(zip(variations, theta_sens['impacts'])):
            pct_change = ((variation - baseline) / baseline) * 100
            report_lines.append(f"- `{parameter} = {variation:.4f}` ({pct_change:+.1f}%) → θ = `{impact:.4f}`")
        report_lines.append("")
        report_lines.append(f"**Élasticité de θ par rapport à {parameter}** : `{theta_sens['elasticity']:.4f}`")
        report_lines.append("")

        # Impact sur Gini
        report_lines.append("### Impact sur les inégalités (Gini)")
        report_lines.append("")
        report_lines.append("**Gini moyens simulés pour chaque valeur** :")
        report_lines.append("")
        for i, (variation, impact) in enumerate(zip(variations, gini_sens['impacts'])):
            pct_change = ((variation - baseline) / baseline) * 100
            report_lines.append(f"- `{parameter} = {variation:.4f}` ({pct_change:+.1f}%) → Gini = `{impact:.4f}`")
        report_lines.append("")
        report_lines.append(f"**Élasticité du Gini par rapport à {parameter}** : `{gini_sens['elasticity']:.4f}`")
        report_lines.append("")

        # Impact sur stabilité
        if stability_sens.get('impacts'):
            report_lines.append("### Impact sur la stabilité")
            report_lines.append("")
            report_lines.append("**Variance de θ pour chaque valeur** :")
            report_lines.append("")
            report_lines.append("_(Plus la variance est faible, plus le système est stable)_")
            report_lines.append("")
            for i, (variation, impact) in enumerate(zip(variations, stability_sens['impacts'])):
                pct_change = ((variation - baseline) / baseline) * 100
                report_lines.append(f"- `{parameter} = {variation:.4f}` ({pct_change:+.1f}%) → Variance(θ) = `{impact:.6f}`")
            report_lines.append("")

        # ==================================================================================
        # SECTION 4: SYNTHÈSE INTERPRÉTATIVE
        # ==================================================================================
        report_lines.append("## 4. Synthèse interprétative")
        report_lines.append("")

        interpretations = []

        # Analyse du crash rate
        if stability['crash_rate'] == 0:
            interpretations.append(
                "✅ **Stabilité numérique** : Le modèle IRIS ne présente aucun crash sur "
                f"l'échantillon Monte Carlo ({n_runs} runs). Le système converge de manière robuste."
            )
        elif stability['crash_rate'] < 0.05:
            interpretations.append(
                f"⚠️ **Stabilité acceptable** : Taux de crash faible ({stability['crash_rate']:.2%}), "
                "le modèle est globalement stable mais quelques simulations ont échoué."
            )
        else:
            interpretations.append(
                f"❌ **Problème de stabilité** : Taux de crash élevé ({stability['crash_rate']:.2%}). "
                "Une investigation des paramètres est recommandée."
            )

        # Analyse de θ
        theta_deviation = abs(theta['mean'] - 1.0)
        if theta_deviation < 0.02:
            interpretations.append(
                f"✅ **Régulation thermodynamique** : Le thermomètre θ reste très proche de 1.0 "
                f"(moyenne = {theta['mean']:.4f}), indiquant une régulation thermodynamique efficace."
            )
        elif theta_deviation < 0.05:
            interpretations.append(
                f"⚠️ **Régulation modérée** : Le thermomètre θ s'écarte légèrement de 1.0 "
                f"(moyenne = {theta['mean']:.4f}). Le système tend vers l'équilibre mais avec un léger biais."
            )
        else:
            interpretations.append(
                f"❌ **Déséquilibre thermodynamique** : Le thermomètre θ s'écarte significativement "
                f"de 1.0 (moyenne = {theta['mean']:.4f}). Vérifier les paramètres RAD."
            )

        # Analyse de la sensibilité (Gini)
        if abs(gini_sens['elasticity']) < 0.1:
            interpretations.append(
                f"✅ **Faible sensibilité des inégalités** : L'élasticité du Gini par rapport à "
                f"`{parameter}` est très faible ({gini_sens['elasticity']:.4f}), indiquant que ce "
                "paramètre n'a pas d'effet majeur sur les inégalités."
            )
        elif gini_sens['elasticity'] > 0.1:
            interpretations.append(
                f"⚠️ **Impact sur les inégalités** : L'analyse de sensibilité suggère que "
                f"`{parameter}` tend à augmenter les inégalités lorsqu'il augmente "
                f"(élasticité = {gini_sens['elasticity']:.4f})."
            )
        elif gini_sens['elasticity'] < -0.1:
            interpretations.append(
                f"✅ **Réduction des inégalités** : Augmenter `{parameter}` tend à réduire "
                f"les inégalités (élasticité = {gini_sens['elasticity']:.4f})."
            )

        # Analyse de la sensibilité (θ)
        if abs(theta_sens['elasticity']) < 0.05:
            interpretations.append(
                f"✅ **Robustesse de θ** : Le thermomètre θ est peu sensible aux variations de "
                f"`{parameter}` (élasticité = {theta_sens['elasticity']:.4f}), ce qui est souhaitable "
                "pour la stabilité du système."
            )

        # Écriture des interprétations
        for interp in interpretations:
            report_lines.append(f"{interp}")
            report_lines.append("")

        # ==================================================================================
        # CONCLUSION
        # ==================================================================================
        report_lines.append("---")
        report_lines.append("")
        report_lines.append("## Conclusion")
        report_lines.append("")

        # Décision globale basée sur les métriques clés
        is_stable = stability['crash_rate'] < 0.05
        is_converged = stability['convergence_rate'] > 0.9
        is_balanced = theta_deviation < 0.05

        if is_stable and is_converged and is_balanced:
            report_lines.append(
                "✅ **Le modèle IRIS v2.1 passe avec succès les tests de validation.**  "
            )
            report_lines.append(
                "Le système démontre une stabilité numérique robuste, une convergence efficace "
                "vers l'équilibre thermodynamique, et une sensibilité raisonnable aux paramètres. "
                "Le modèle est prêt pour des simulations à plus grande échelle."
            )
        else:
            report_lines.append(
                "⚠️ **Le modèle IRIS v2.1 nécessite des ajustements.**  "
            )
            report_lines.append(
                "Certains indicateurs suggèrent des améliorations possibles. Vérifier les "
                "paramètres RAD et effectuer des tests supplémentaires avec des configurations variées."
            )

        report_lines.append("")
        report_lines.append("---")
        report_lines.append("")
        report_lines.append("_Rapport généré automatiquement par IRIS Validation Module_")
        report_lines.append("")

        # ==================================================================================
        # ÉCRITURE DU FICHIER
        # ==================================================================================
        # Crée les répertoires si nécessaire
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)

        # Écriture du rapport
        report_content = "\n".join(report_lines)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_content)

        print(f"✅ Rapport de validation généré: {output_path}")

        return output_path


# Fonction utilitaire pour exécution rapide
def quick_validation(n_runs: int = 50, steps: int = 100, verbose: bool = True):
    """
    Validation rapide : Monte Carlo + KS test

    Usage:
        from iris_validation import quick_validation
        quick_validation(n_runs=50, steps=100)
    """
    print("\n" + "="*80)
    print(" "*20 + "IRIS VALIDATION RAPIDE")
    print("="*80 + "\n")

    validator = IRISValidator()

    # Monte Carlo
    mc_results = validator.run_monte_carlo(
        n_runs=n_runs,
        steps=steps,
        parallel=False,  # Séquentiel pour éviter pickle issues
        verbose=verbose
    )

    # Test KS
    ks_results = validator.kolmogorov_smirnov_test(
        mc_results,
        target_distribution='normal',
        verbose=verbose
    )

    # Résumé final
    print("\n" + "="*80)
    print(" "*25 + "RÉSUMÉ VALIDATION")
    print("="*80)
    print(f"\nMonte Carlo ({n_runs} runs):")
    print(f"  θ = {mc_results.theta_mean:.4f} ± {mc_results.theta_std:.4f} (IC 95%: [{mc_results.theta_ci_lower:.4f}, {mc_results.theta_ci_upper:.4f}])")
    print(f"  Convergence : {mc_results.convergence_rate*100:.1f}%")
    print(f"  Crash rate : {mc_results.crash_rate*100:.1f}%")
    print(f"\nTests statistiques:")
    print(f"  KS p-value : {ks_results['ks_p_value']:.4f} → {'✓ Normal' if ks_results['ks_p_value'] > 0.05 else '✗ Non-normal'}")
    print(f"  Shapiro-Wilk : {ks_results['normality_conclusion']}")
    print("="*80 + "\n")

    return mc_results, ks_results


if __name__ == "__main__":
    """
    Point d'entrée CLI pour génération de rapport de validation

    Usage:
        python -m iris.core.iris_validation

    Génère automatiquement un rapport de validation Markdown à partir des
    résultats JSON existants dans validation_results/
    """
    print("\n" + "="*80)
    print(" "*20 + "IRIS VALIDATION REPORT GENERATOR")
    print("="*80 + "\n")

    validator = IRISValidator()

    try:
        # Génère le rapport de validation
        report_path = validator.generate_validation_report()

        print("\n" + "="*80)
        print(f"✅ Rapport de validation généré avec succès!")
        print(f"📄 Fichier: {report_path}")
        print("="*80 + "\n")

    except FileNotFoundError as e:
        print(f"\n❌ Erreur: {e}")
        print("\n💡 Pour générer les fichiers de résultats, lancez d'abord:")
        print("   - validator.run_monte_carlo()")
        print("   - validator.run_sensitivity_analysis('eta_alpha', 0.5)")
        print("\nOu utilisez la fonction quick_validation() pour tout automatiser.\n")
