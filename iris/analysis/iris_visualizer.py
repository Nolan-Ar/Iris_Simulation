"""
IRIS Economic System - Visualization Module
===========================================

Module de visualisation pour l'analyse du système IRIS.

Auteur: Arnault Nolan
Email: arnaultnolan@gmail.com
Date: 2025

Génère des graphiques illustrant :
- L'évolution des variables clés (V, U, D)
- Le fonctionnement des mécanismes de régulation (θ, κ)
- La stabilité du système (indicateur centré)
- Les métriques d'équité (Gini) et de liquidité (taux de circulation)
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
from typing import Dict, List
import json


# Configuration du style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 10)
plt.rcParams['font.size'] = 10


class IRISVisualizer:
    """Classe pour generer les visualisations du systeme IRIS"""

    def __init__(self, output_dir: str = "results", safe_mode: bool = False):
        """
        Initialise le visualiseur

        Args:
            output_dir: Repertoire de sortie pour les graphiques
            safe_mode: Mode securise (desactive viz en cas d'erreur, retourne silencieusement)
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.safe_mode = safe_mode
        self.viz_errors = []  # Liste des erreurs de visualisation

    def _safe_savefig(self, fig, output_path, dpi=300):
        """
        Sauvegarde securisee d'une figure avec gestion d'erreurs

        Args:
            fig: Figure matplotlib
            output_path: Chemin de sortie
            dpi: Resolution

        Returns:
            bool: True si succes, False si erreur
        """
        try:
            fig.savefig(output_path, dpi=dpi, bbox_inches='tight')
            print(f"OK: Graphique sauvegarde : {output_path}")
            return True
        except Exception as e:
            error_msg = f"ERREUR visualisation {output_path}: {str(e)}"
            self.viz_errors.append(error_msg)
            if not self.safe_mode:
                print(f"ATTENTION: {error_msg}")
            return False
        finally:
            plt.close(fig)

    def plot_main_variables(self, history: Dict, title: str = "Évolution des variables IRIS"):
        """
        Graphique de l'évolution de V, U, D dans le temps

        Args:
            history: Historique de la simulation
            title: Titre du graphique
        """
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle(title, fontsize=16, fontweight='bold')

        time = history['time']

        # 1. Variables principales (V, U, D)
        ax1 = axes[0, 0]
        ax1.plot(time, history['total_V'], label='V (Verum - Mémoire)', linewidth=2, color='#2E86AB')
        ax1.plot(time, history['total_U'], label='U (Usage - Monnaie)', linewidth=2, color='#A23B72')
        ax1.plot(time, history['total_D'], label='D (Dette thermométrique)', linewidth=2,
                 color='#F18F01', linestyle='--')
        ax1.set_xlabel('Temps')
        ax1.set_ylabel('Montant total')
        ax1.set_title('Évolution des Variables Économiques')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # 2. Thermomètre et Indicateur
        ax2 = axes[0, 1]
        ax2_twin = ax2.twinx()

        ax2.plot(time, history['thermometer'], label='Thermomètre θ = D/V',
                linewidth=2, color='#E63946')
        ax2.axhline(y=1.0, color='green', linestyle='--', alpha=0.5, label='Équilibre (θ=1)')
        ax2.set_xlabel('Temps')
        ax2.set_ylabel('Thermomètre θ', color='#E63946')
        ax2.tick_params(axis='y', labelcolor='#E63946')
        ax2.set_title('Régulation Thermométrique')
        ax2.grid(True, alpha=0.3)

        ax2_twin.plot(time, history['indicator'], label='Indicateur I = θ-1',
                     linewidth=2, color='#457B9D', alpha=0.7)
        ax2_twin.axhline(y=0.0, color='green', linestyle='--', alpha=0.5)
        ax2_twin.set_ylabel('Indicateur I', color='#457B9D')
        ax2_twin.tick_params(axis='y', labelcolor='#457B9D')

        # Légendes combinées
        lines1, labels1 = ax2.get_legend_handles_labels()
        lines2, labels2 = ax2_twin.get_legend_handles_labels()
        ax2.legend(lines1 + lines2, labels1 + labels2, loc='upper right')

        # 3. Coefficients de régulation κ et η
        ax3 = axes[1, 0]
        ax3.plot(time, history['kappa'], label='κ (conversion V→U)',
                linewidth=2, color='#06A77D', alpha=0.8)

        # Ajoute η si disponible dans l'historique
        if 'eta' in history and len(history['eta']) > 0:
            ax3.plot(time, history['eta'], label='η (rendement S+U→V)',
                    linewidth=2, color='#9D4EDD', alpha=0.8, linestyle='-')

        ax3.axhline(y=1.0, color='gray', linestyle='--', alpha=0.5, label='Équilibre (1.0)')
        ax3.set_xlabel('Temps')
        ax3.set_ylabel('Coefficients de régulation')
        ax3.set_title('Mécanismes de Régulation Thermodynamique (κ et η)')
        ax3.legend(loc='best')
        ax3.grid(True, alpha=0.3)
        ax3.set_ylim([0.5, 1.5])  # Bornes autour de 1.0 pour mieux voir les variations

        # 4. Métriques sociales (Gini et Circulation)
        ax4 = axes[1, 1]
        ax4_twin = ax4.twinx()

        ax4.plot(time, history['gini_coefficient'], label='Coefficient de Gini',
                linewidth=2, color='#D62828')
        ax4.set_xlabel('Temps')
        ax4.set_ylabel('Coefficient de Gini', color='#D62828')
        ax4.tick_params(axis='y', labelcolor='#D62828')
        ax4.set_title('Équité et Liquidité du Système')
        ax4.set_ylim([0, 1])

        ax4_twin.plot(time, history['circulation_rate'], label='Taux de circulation U/V',
                     linewidth=2, color='#F77F00', alpha=0.7)
        ax4_twin.set_ylabel('Taux de circulation', color='#F77F00')
        ax4_twin.tick_params(axis='y', labelcolor='#F77F00')

        lines1, labels1 = ax4.get_legend_handles_labels()
        lines2, labels2 = ax4_twin.get_legend_handles_labels()
        ax4.legend(lines1 + lines2, labels1 + labels2, loc='upper right')
        ax4.grid(True, alpha=0.3)

        plt.tight_layout()
        output_path = self.output_dir / f"{title.replace(' ', '_')}.png"
        self._safe_savefig(fig, output_path)

    def plot_regulation_detail(self, history: Dict):
        """
        Graphique détaillé du mécanisme de régulation

        Args:
            history: Historique de la simulation
        """
        fig, axes = plt.subplots(2, 1, figsize=(14, 10))
        fig.suptitle('Analyse Détaillée de la Régulation IRIS', fontsize=16, fontweight='bold')

        time = history['time']

        # 1. Relation entre θ, κ et η (rétroactions contracycliques)
        ax1 = axes[0]
        color1 = '#E63946'
        color2 = '#06A77D'
        color3 = '#9D4EDD'

        ax1.set_xlabel('Temps')
        ax1.set_ylabel('Thermomètre θ', color=color1)
        line1 = ax1.plot(time, history['thermometer'], linewidth=2, color=color1,
                         label='Thermomètre θ')
        ax1.tick_params(axis='y', labelcolor=color1)
        ax1.axhline(y=1.0, color='gray', linestyle='--', alpha=0.5)
        ax1.grid(True, alpha=0.3)

        ax1_twin = ax1.twinx()
        ax1_twin.set_ylabel('Coefficients κ et η', color=color2)
        line2 = ax1_twin.plot(time, history['kappa'], linewidth=2, color=color2,
                             label='Coefficient κ (V→U)', alpha=0.8)

        # Ajoute η si disponible
        if 'eta' in history and len(history['eta']) > 0:
            line3 = ax1_twin.plot(time, history['eta'], linewidth=2, color=color3,
                                 label='Coefficient η (S+U→V)', alpha=0.8, linestyle='--')
        else:
            line3 = []

        ax1_twin.tick_params(axis='y', labelcolor=color2)
        ax1_twin.axhline(y=1.0, color='gray', linestyle='--', alpha=0.5)

        # Légende combinée
        lines = line1 + line2 + line3
        labels = [l.get_label() for l in lines]
        ax1.legend(lines, labels, loc='best')
        ax1.set_title('Boucles de Rétroaction Contracycliques (θ, κ, η)')

        # 2. Stabilité : écart-type glissant de l'indicateur
        window = 50
        if len(history['indicator']) > window:
            indicator_array = np.array(history['indicator'])
            rolling_std = np.array([
                np.std(indicator_array[max(0, i-window):i+1])
                for i in range(len(indicator_array))
            ])

            ax2 = axes[1]
            ax2.plot(time, np.abs(indicator_array), label='|Indicateur I|',
                    linewidth=1, color='#457B9D', alpha=0.5)
            ax2.plot(time, rolling_std, label=f'Écart-type glissant (fenêtre={window})',
                    linewidth=2, color='#F18F01')
            ax2.set_xlabel('Temps')
            ax2.set_ylabel('Volatilité')
            ax2.set_title('Mesure de la Stabilité du Système')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            ax2.set_yscale('log')

        plt.tight_layout()
        output_path = self.output_dir / "regulation_detail.png"
        self._safe_savefig(fig, output_path)

    def plot_shock_comparison(self, histories: Dict[str, Dict], shock_time: int):
        """
        Compare l'évolution avant/après choc

        Args:
            histories: Dictionnaire des historiques {scenario_name: history}
            shock_time: Moment du choc
        """
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Résilience IRIS face aux Chocs Économiques', fontsize=16, fontweight='bold')

        colors = ['#2E86AB', '#E63946', '#06A77D', '#F18F01']

        for idx, (scenario_name, history) in enumerate(histories.items()):
            time = history['time']
            color = colors[idx % len(colors)]

            # 1. Thermomètre
            ax1 = axes[0, 0]
            ax1.plot(time, history['thermometer'], label=scenario_name,
                    linewidth=2, color=color)
            ax1.axvline(x=shock_time, color='red', linestyle='--', alpha=0.3)
            ax1.axhline(y=1.0, color='gray', linestyle='--', alpha=0.3)
            ax1.set_xlabel('Temps')
            ax1.set_ylabel('Thermomètre θ')
            ax1.set_title('Évolution du Thermomètre')
            ax1.legend()
            ax1.grid(True, alpha=0.3)

            # 2. Indicateur centré
            ax2 = axes[0, 1]
            ax2.plot(time, history['indicator'], label=scenario_name,
                    linewidth=2, color=color)
            ax2.axvline(x=shock_time, color='red', linestyle='--', alpha=0.3)
            ax2.axhline(y=0.0, color='gray', linestyle='--', alpha=0.3)
            ax2.set_xlabel('Temps')
            ax2.set_ylabel('Indicateur I')
            ax2.set_title('Indicateur Centré (Déviation)')
            ax2.legend()
            ax2.grid(True, alpha=0.3)

            # 3. Coefficient κ
            ax3 = axes[1, 0]
            ax3.plot(time, history['kappa'], label=scenario_name,
                    linewidth=2, color=color)
            ax3.axvline(x=shock_time, color='red', linestyle='--', alpha=0.3)
            ax3.axhline(y=1.0, color='gray', linestyle='--', alpha=0.3)
            ax3.set_xlabel('Temps')
            ax3.set_ylabel('Coefficient κ')
            ax3.set_title('Réponse du Régulateur')
            ax3.legend()
            ax3.grid(True, alpha=0.3)

            # 4. Gini
            ax4 = axes[1, 1]
            ax4.plot(time, history['gini_coefficient'], label=scenario_name,
                    linewidth=2, color=color)
            ax4.axvline(x=shock_time, color='red', linestyle='--', alpha=0.3)
            ax4.set_xlabel('Temps')
            ax4.set_ylabel('Coefficient de Gini')
            ax4.set_title('Évolution des Inégalités')
            ax4.legend()
            ax4.grid(True, alpha=0.3)
            ax4.set_ylim([0, 1])

        plt.tight_layout()
        output_path = self.output_dir / "shock_comparison.png"
        self._safe_savefig(fig, output_path)

    def plot_phase_space(self, history: Dict):
        """
        Diagramme de phase : θ vs κ

        Args:
            history: Historique de la simulation
        """
        fig, ax = plt.subplots(figsize=(10, 10))

        theta = np.array(history['thermometer'])
        kappa = np.array(history['kappa'])
        time = np.array(history['time'])

        # Gradient de couleur selon le temps
        scatter = ax.scatter(theta, kappa, c=time, cmap='viridis',
                           s=20, alpha=0.6, edgecolors='black', linewidth=0.5)

        # Point d'équilibre
        ax.plot(1.0, 1.0, 'r*', markersize=20, label='Équilibre (θ=1, κ=1)')

        # Lignes de référence
        ax.axvline(x=1.0, color='gray', linestyle='--', alpha=0.3)
        ax.axhline(y=1.0, color='gray', linestyle='--', alpha=0.3)

        ax.set_xlabel('Thermomètre θ = D/V', fontsize=12)
        ax.set_ylabel('Coefficient κ (V→U)', fontsize=12)
        ax.set_title('Espace des Phases : Régulation IRIS', fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # Barre de couleur
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label('Temps', rotation=270, labelpad=20)

        plt.tight_layout()
        output_path = self.output_dir / "phase_space.png"
        self._safe_savefig(fig, output_path)

    def plot_demographics(self, history: Dict):
        """
        Graphique de l'evolution demographique

        Affiche :
        - Evolution de la population totale
        - Naissances et deces cumulatifs
        - Age moyen de la population

        Args:
            history: Historique de la simulation
        """
        if 'population' not in history or not any(history['population']):
            print("ATTENTION: Pas de donnees demographiques a visualiser")
            return

        fig, axes = plt.subplots(3, 1, figsize=(12, 10))
        time = history['time']

        # 1. Population totale
        ax = axes[0]
        ax.plot(time, history['population'], 'b-', linewidth=2, label='Population totale')
        ax.set_ylabel('Nombre d\'agents')
        ax.set_title('Evolution de la population', fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # 2. Naissances et deces
        ax = axes[1]
        births_cumulative = np.cumsum(history['births'])
        deaths_cumulative = np.cumsum(history['deaths'])

        ax.plot(time, births_cumulative, 'g-', linewidth=2, label='Naissances cumulees')
        ax.plot(time, deaths_cumulative, 'r-', linewidth=2, label='Deces cumules')
        ax.set_ylabel('Nombre cumule')
        ax.set_title('Naissances et deces', fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # 3. Age moyen
        ax = axes[2]
        if any(history['avg_age']):
            ax.plot(time, history['avg_age'], 'purple', linewidth=2, label='Age moyen')
            ax.axhline(y=40, color='gray', linestyle='--', alpha=0.5, label='Ref: 40 ans')
            ax.set_ylabel('Age (annees)')
            ax.set_xlabel('Temps (annees)')
            ax.set_title('Age moyen de la population', fontweight='bold')
            ax.legend()
            ax.grid(True, alpha=0.3)

        plt.tight_layout()
        output_path = self.output_dir / "demographics.png"
        self._safe_savefig(fig, output_path)

    def plot_long_term_resilience(self, history: Dict):
        """
        Graphique de la resilience a long terme

        Affiche :
        - Catastrophes sur la timeline
        - Evolution du thermometre avec marqueurs de catastrophes
        - Impact sur la richesse totale (V + U)

        Args:
            history: Historique de la simulation
        """
        if 'catastrophes' not in history:
            print("ATTENTION: Pas de donnees de catastrophes a visualiser")
            return

        fig, axes = plt.subplots(3, 1, figsize=(12, 10))
        time = history['time']

        # Indices des catastrophes
        catastrophe_times = [t for t, c in zip(time, history['catastrophes']) if c > 0]

        # 1. Thermometre avec marqueurs de catastrophes
        ax = axes[0]
        ax.plot(time, history['thermometer'], 'b-', linewidth=1.5, label='Thermometre θ')
        ax.axhline(y=1.0, color='green', linestyle='--', alpha=0.5, label='Equilibre θ=1.0')

        # Marque les catastrophes
        for cat_time in catastrophe_times:
            ax.axvline(x=cat_time, color='red', alpha=0.3, linewidth=1)

        ax.set_ylabel('θ = D/V')
        ax.set_title('Thermometre avec evenements catastrophiques', fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # 2. Richesse totale (V + U)
        ax = axes[1]
        total_wealth = np.array(history['total_V']) + np.array(history['total_U'])
        ax.plot(time, total_wealth, 'darkgreen', linewidth=2, label='Richesse totale (V+U)')

        # Marque les catastrophes
        for cat_time in catastrophe_times:
            ax.axvline(x=cat_time, color='red', alpha=0.3, linewidth=1, label='Catastrophe' if cat_time == catastrophe_times[0] else '')

        ax.set_ylabel('Richesse totale')
        ax.set_title('Impact des catastrophes sur la richesse', fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # 3. Nombre de catastrophes par periode
        ax = axes[2]
        catastrophes_cumul = np.cumsum(history['catastrophes'])
        ax.plot(time, catastrophes_cumul, 'r-', linewidth=2, label='Catastrophes cumulees')
        ax.fill_between(time, catastrophes_cumul, alpha=0.3, color='red')
        ax.set_ylabel('Nombre cumule')
        ax.set_xlabel('Temps (annees)')
        ax.set_title('Cumul des catastrophes', fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        output_path = self.output_dir / "long_term_resilience.png"
        self._safe_savefig(fig, output_path)

    def export_data(self, history: Dict, filename: str = "simulation_data"):
        """
        Exporte les données de simulation en CSV et JSON

        Args:
            history: Historique de la simulation
            filename: Nom de base du fichier
        """
        import pandas as pd

        # Conversion en DataFrame
        df = pd.DataFrame(history)

        # Export CSV
        csv_path = self.output_dir / f"{filename}.csv"
        df.to_csv(csv_path, index=False)
        print(f"OK: Données CSV exportées : {csv_path}")

        # Export JSON
        json_path = self.output_dir / f"{filename}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2)
        print(f"OK: Données JSON exportées : {json_path}")

    def generate_report(self, history: Dict, scenario_name: str = "baseline"):
        """
        Génère un rapport complet d'analyse

        Args:
            history: Historique de la simulation
            scenario_name: Nom du scénario
        """
        print(f"\n{'='*60}")
        print(f"RAPPORT D'ANALYSE - Scénario : {scenario_name}")
        print(f"{'='*60}\n")

        # Statistiques générales
        print("STATISTIQUES GÉNÉRALES")
        print(f"  Durée de simulation : {history['time'][-1]} pas de temps")
        print(f"  V total final : {history['total_V'][-1]:.2f}")
        print(f"  U total final : {history['total_U'][-1]:.2f}")
        print(f"  D total final : {history['total_D'][-1]:.2f}")
        print()

        # Métriques de régulation
        theta_array = np.array(history['thermometer'])
        indicator_array = np.array(history['indicator'])
        kappa_array = np.array(history['kappa'])

        print("🎯 MÉTRIQUES DE RÉGULATION")
        print(f"  Thermomètre θ moyen : {theta_array.mean():.4f} (cible: 1.0000)")
        print(f"  Thermomètre θ écart-type : {theta_array.std():.4f}")
        print(f"  Indicateur I moyen : {indicator_array.mean():.4f} (cible: 0.0000)")
        print(f"  Indicateur I écart-type : {indicator_array.std():.4f}")
        print(f"  Coefficient κ moyen : {kappa_array.mean():.4f}")
        print(f"  Coefficient κ écart-type : {kappa_array.std():.4f}")
        print()

        # Métriques sociales
        gini_array = np.array(history['gini_coefficient'])
        circ_array = np.array(history['circulation_rate'])

        print("🤝 MÉTRIQUES SOCIALES")
        print(f"  Gini initial : {gini_array[0]:.4f}")
        print(f"  Gini final : {gini_array[-1]:.4f}")
        print(f"  Gini moyen : {gini_array.mean():.4f}")
        print(f"  Taux de circulation U/V final : {circ_array[-1]:.4f}")
        print()

        # Stabilité
        print("🔒 STABILITÉ DU SYSTÈME")
        deviation_95 = np.percentile(np.abs(indicator_array), 95)
        print(f"  95% des déviations < {deviation_95:.4f}")

        # Temps de retour à l'équilibre (après choc si présent)
        equilibrium_threshold = 0.05
        out_of_equilibrium = np.abs(indicator_array) > equilibrium_threshold
        if out_of_equilibrium.any():
            # Trouve les périodes hors équilibre
            in_equilibrium = ~out_of_equilibrium
            if in_equilibrium.any():
                print(f"  Seuil d'équilibre : |I| < {equilibrium_threshold}")
                print(f"  Système en équilibre : {in_equilibrium.sum() / len(indicator_array) * 100:.1f}% du temps")
        print()

        print(f"{'='*60}\n")


def create_dashboard(history: Dict, output_dir: str = "results"):
    """
    Crée un dashboard complet avec toutes les visualisations

    Args:
        history: Historique de la simulation
        output_dir: Répertoire de sortie
    """
    viz = IRISVisualizer(output_dir)

    print("\nGénération des visualisations...")

    viz.plot_main_variables(history)
    viz.plot_regulation_detail(history)
    viz.plot_phase_space(history)

    # Visualisations démographiques (si disponibles)
    if 'population' in history and any(history['population']):
        viz.plot_demographics(history)

    # Visualisations de résilience long terme (si catastrophes)
    if 'catastrophes' in history:
        viz.plot_long_term_resilience(history)

    viz.export_data(history)
    viz.generate_report(history)

    print("OK: Dashboard complet généré")
