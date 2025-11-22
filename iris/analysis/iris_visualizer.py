"""
IRIS Visualizer
===============

Outil de visualisation pour les simulations IRIS.
"""

from typing import Dict, List, Any
from pathlib import Path
import json

try:
    import matplotlib
    matplotlib.use('Agg')  # Backend non-interactif
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


class IRISVisualizer:
    """Visualisateur pour les simulations IRIS."""

    def __init__(self, output_dir: str = "results"):
        """
        Initialise le visualisateur.

        Args:
            output_dir: Répertoire de sortie pour les graphiques
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def plot_main_variables(self, history: Dict[str, List]) -> None:
        """
        Crée les graphiques des variables principales.

        Args:
            history: Dictionnaire avec l'historique de la simulation
        """
        if not MATPLOTLIB_AVAILABLE:
            print("⚠ matplotlib non disponible - graphiques désactivés")
            return

        # Graphique 4 subplots
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Variables principales IRIS', fontsize=16, fontweight='bold')

        time = history.get('time', range(len(history['thermometer'])))

        # Subplot 1: Thermomètre θ
        ax = axes[0, 0]
        ax.plot(time, history['thermometer'], label='θ', linewidth=1.5)
        ax.axhline(y=1.0, color='r', linestyle='--', linewidth=1, label='Cible (θ=1)')
        ax.set_xlabel('Temps (mois)')
        ax.set_ylabel('θ')
        ax.set_title('Thermomètre θ = D/V_on')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # Subplot 2: Coefficients κ et η
        ax = axes[0, 1]
        ax.plot(time, history['kappa'], label='κ (kappa)', linewidth=1.5)
        ax.plot(time, history['eta'], label='η (eta)', linewidth=1.5)
        ax.axhline(y=1.0, color='gray', linestyle='--', linewidth=0.8, alpha=0.5)
        ax.set_xlabel('Temps (mois)')
        ax.set_ylabel('Coefficient')
        ax.set_title('Coefficients de régulation κ et η')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # Subplot 3: Population
        ax = axes[1, 0]
        ax.plot(time, history['population'], label='Population', linewidth=1.5, color='green')
        ax.set_xlabel('Temps (mois)')
        ax.set_ylabel('Nombre d\'agents')
        ax.set_title('Évolution de la population')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # Subplot 4: Gini
        ax = axes[1, 1]
        ax.plot(time, history['gini_coefficient'], label='Gini', linewidth=1.5, color='purple')
        ax.set_xlabel('Temps (mois)')
        ax.set_ylabel('Coefficient de Gini')
        ax.set_title('Inégalité de richesse (Gini)')
        ax.legend()
        ax.grid(True, alpha=0.3)

        plt.tight_layout()

        # Sauvegarde
        output_path = self.output_dir / "main_variables.png"
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close(fig)

        print(f"  ✓ Graphique sauvegardé: {output_path}")

    def export_data(self, history: Dict[str, List], filename: str = "data") -> None:
        """
        Exporte les données en JSON.

        Args:
            history: Historique de la simulation
            filename: Nom du fichier (sans extension)
        """
        output_path = self.output_dir / f"{filename}.json"

        # Conversion des arrays numpy en listes si nécessaire
        cleaned_history = {}
        for key, value in history.items():
            if hasattr(value, 'tolist'):  # numpy array
                cleaned_history[key] = value.tolist()
            else:
                cleaned_history[key] = value

        with open(output_path, 'w') as f:
            json.dump(cleaned_history, f, indent=2)

        print(f"  ✓ Données exportées: {output_path}")
