"""
IRIS Plot Analysis
==================

Génération de graphiques d'analyse comparative pour les expériences IRIS.

Usage:
    python -m iris.simulations.plot_analysis results/test_grid
"""

import sys
from pathlib import Path
from typing import Optional, List
import warnings

import pandas as pd
import numpy as np

# Import matplotlib avec backend non-interactif
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

# Configuration style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10

# Suppression warnings
warnings.filterwarnings('ignore')


class IRISPlotAnalysis:
    """Générateur de graphiques d'analyse pour les expériences IRIS."""

    def __init__(self, results_dir: Path):
        """
        Initialise l'analyseur de graphiques.

        Args:
            results_dir: Répertoire contenant summary.csv
        """
        self.results_dir = Path(results_dir)
        self.summary_path = self.results_dir / "summary.csv"
        self.plots_dir = self.results_dir / "plots"
        self.plots_dir.mkdir(exist_ok=True)

        # Chargement des données
        if not self.summary_path.exists():
            raise FileNotFoundError(f"Fichier summary.csv introuvable: {self.summary_path}")

        self.df = pd.read_csv(self.summary_path)
        print(f"✓ Chargé {len(self.df)} scénarios depuis {self.summary_path}")

    def plot_all(self) -> None:
        """Génère tous les graphiques d'analyse."""
        print(f"\n{'='*80}")
        print(f"GÉNÉRATION DES GRAPHIQUES D'ANALYSE")
        print(f"{'='*80}\n")

        plots_generated = []

        # 1. Vue d'ensemble
        print("📊 1. Vue d'ensemble...")
        self.plot_overview()
        plots_generated.append("overview.png")

        # 2. Effet de la population
        print("📊 2. Effet de la population initiale...")
        self.plot_population_effect()
        plots_generated.append("population_effect.png")

        # 3. Effet des catastrophes
        if 'enable_catastrophes' in self.df.columns:
            print("📊 3. Effet des catastrophes...")
            self.plot_catastrophes_effect()
            plots_generated.append("catastrophes_effect.png")

        # 4. Effet du taux de conservation
        if 'conservation_rate' in self.df.columns:
            print("📊 4. Effet du taux de conservation ρ...")
            self.plot_conservation_effect()
            plots_generated.append("conservation_effect.png")

        # 5. Convergence vs Stabilité
        print("📊 5. Convergence vs Stabilité...")
        self.plot_convergence_stability()
        plots_generated.append("convergence_stability.png")

        # 6. Distribution des métriques
        print("📊 6. Distribution des métriques...")
        self.plot_metrics_distribution()
        plots_generated.append("metrics_distribution.png")

        # 7. Corrélations
        print("📊 7. Matrice de corrélation...")
        self.plot_correlation_matrix()
        plots_generated.append("correlation_matrix.png")

        # 8. Scénarios optimaux
        print("📊 8. Comparaison scénarios optimaux...")
        self.plot_best_scenarios()
        plots_generated.append("best_scenarios.png")

        # 9. Évolution temporelle (si plusieurs durées)
        if 'steps' in self.df.columns and self.df['steps'].nunique() > 1:
            print("📊 9. Effet de la durée de simulation...")
            self.plot_duration_effect()
            plots_generated.append("duration_effect.png")

        # 10. Heatmap 2D (si assez de données)
        if len(self.df) >= 9:
            print("📊 10. Heatmaps 2D...")
            self.plot_heatmaps()
            plots_generated.append("heatmaps.png")

        print(f"\n{'='*80}")
        print(f"✅ {len(plots_generated)} graphiques générés dans: {self.plots_dir}")
        print(f"{'='*80}\n")

        for plot_name in plots_generated:
            print(f"  ✓ {plot_name}")

    def plot_overview(self) -> None:
        """Graphique de vue d'ensemble (4 subplots)."""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Vue d\'ensemble des résultats - IRIS', fontsize=16, fontweight='bold')

        # 1. Distribution θ_mean
        ax = axes[0, 0]
        ax.hist(self.df['theta_mean'], bins=20, color='steelblue', alpha=0.7, edgecolor='black')
        ax.axvline(1.0, color='red', linestyle='--', linewidth=2, label='Cible (θ=1)')
        ax.set_xlabel('θ moyen')
        ax.set_ylabel('Fréquence')
        ax.set_title('Distribution de θ moyen')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # 2. Distribution θ_std
        ax = axes[0, 1]
        ax.hist(self.df['theta_std'], bins=20, color='coral', alpha=0.7, edgecolor='black')
        ax.set_xlabel('θ écart-type')
        ax.set_ylabel('Fréquence')
        ax.set_title('Distribution de la stabilité (θ_std)')
        ax.grid(True, alpha=0.3)

        # 3. Distribution Gini
        ax = axes[1, 0]
        ax.hist(self.df['gini_final'], bins=20, color='purple', alpha=0.7, edgecolor='black')
        ax.set_xlabel('Gini final')
        ax.set_ylabel('Fréquence')
        ax.set_title('Distribution des inégalités (Gini)')
        ax.grid(True, alpha=0.3)

        # 4. Scatter θ_mean vs Gini
        ax = axes[1, 1]
        scatter = ax.scatter(self.df['theta_mean'], self.df['gini_final'],
                            c=self.df['theta_std'], cmap='viridis',
                            s=100, alpha=0.6, edgecolor='black')
        ax.axvline(1.0, color='red', linestyle='--', alpha=0.5)
        ax.set_xlabel('θ moyen')
        ax.set_ylabel('Gini final')
        ax.set_title('Convergence θ vs Inégalités')
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label('θ std (stabilité)')
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        output_path = self.plots_dir / "overview.png"
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close(fig)

    def plot_population_effect(self) -> None:
        """Effet de la population initiale."""
        if 'initial_agents' not in self.df.columns:
            return

        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Effet de la population initiale', fontsize=16, fontweight='bold')

        pop_values = sorted(self.df['initial_agents'].unique())

        # 1. θ_std par population
        ax = axes[0, 0]
        data_by_pop = [self.df[self.df['initial_agents'] == pop]['theta_std'] for pop in pop_values]
        positions = range(len(pop_values))
        bp = ax.boxplot(data_by_pop, positions=positions, labels=[str(p) for p in pop_values],
                        patch_artist=True)
        for patch in bp['boxes']:
            patch.set_facecolor('lightblue')
        ax.set_xlabel('Population initiale')
        ax.set_ylabel('θ std (stabilité)')
        ax.set_title('Stabilité par population')
        ax.grid(True, alpha=0.3, axis='y')

        # 2. θ_mean par population
        ax = axes[0, 1]
        data_by_pop = [self.df[self.df['initial_agents'] == pop]['theta_mean'] for pop in pop_values]
        bp = ax.boxplot(data_by_pop, positions=positions, labels=[str(p) for p in pop_values],
                        patch_artist=True)
        for patch in bp['boxes']:
            patch.set_facecolor('lightcoral')
        ax.axhline(1.0, color='red', linestyle='--', linewidth=1.5, label='Cible')
        ax.set_xlabel('Population initiale')
        ax.set_ylabel('θ moyen')
        ax.set_title('Convergence θ par population')
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')

        # 3. Gini par population
        ax = axes[1, 0]
        data_by_pop = [self.df[self.df['initial_agents'] == pop]['gini_final'] for pop in pop_values]
        bp = ax.boxplot(data_by_pop, positions=positions, labels=[str(p) for p in pop_values],
                        patch_artist=True)
        for patch in bp['boxes']:
            patch.set_facecolor('mediumpurple')
        ax.set_xlabel('Population initiale')
        ax.set_ylabel('Gini final')
        ax.set_title('Inégalités par population')
        ax.grid(True, alpha=0.3, axis='y')

        # 4. Population finale moyenne par population initiale
        ax = axes[1, 1]
        pop_final_mean = [self.df[self.df['initial_agents'] == pop]['population_final'].mean()
                          for pop in pop_values]
        bars = ax.bar(range(len(pop_values)), pop_final_mean, color='green', alpha=0.7,
                      edgecolor='black')
        ax.plot(range(len(pop_values)), pop_values, 'ro-', linewidth=2, markersize=8,
                label='Population initiale')
        ax.set_xticks(range(len(pop_values)))
        ax.set_xticklabels([str(p) for p in pop_values])
        ax.set_xlabel('Population initiale')
        ax.set_ylabel('Population finale (moyenne)')
        ax.set_title('Croissance démographique')
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        output_path = self.plots_dir / "population_effect.png"
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close(fig)

    def plot_catastrophes_effect(self) -> None:
        """Effet des catastrophes."""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Effet des catastrophes', fontsize=16, fontweight='bold')

        with_cata = self.df[self.df['enable_catastrophes'] == True]
        without_cata = self.df[self.df['enable_catastrophes'] == False]

        # 1. θ_std comparaison
        ax = axes[0, 0]
        data = [without_cata['theta_std'], with_cata['theta_std']]
        bp = ax.boxplot(data, labels=['OFF', 'ON'], patch_artist=True)
        bp['boxes'][0].set_facecolor('lightgreen')
        bp['boxes'][1].set_facecolor('salmon')
        ax.set_xlabel('Catastrophes')
        ax.set_ylabel('θ std (stabilité)')
        ax.set_title('Stabilité avec/sans catastrophes')
        ax.grid(True, alpha=0.3, axis='y')

        # 2. θ_mean comparaison
        ax = axes[0, 1]
        data = [without_cata['theta_mean'], with_cata['theta_mean']]
        bp = ax.boxplot(data, labels=['OFF', 'ON'], patch_artist=True)
        bp['boxes'][0].set_facecolor('lightgreen')
        bp['boxes'][1].set_facecolor('salmon')
        ax.axhline(1.0, color='red', linestyle='--', linewidth=1.5, label='Cible')
        ax.set_xlabel('Catastrophes')
        ax.set_ylabel('θ moyen')
        ax.set_title('Convergence θ avec/sans catastrophes')
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')

        # 3. Gini comparaison
        ax = axes[1, 0]
        data = [without_cata['gini_final'], with_cata['gini_final']]
        bp = ax.boxplot(data, labels=['OFF', 'ON'], patch_artist=True)
        bp['boxes'][0].set_facecolor('lightgreen')
        bp['boxes'][1].set_facecolor('salmon')
        ax.set_xlabel('Catastrophes')
        ax.set_ylabel('Gini final')
        ax.set_title('Inégalités avec/sans catastrophes')
        ax.grid(True, alpha=0.3, axis='y')

        # 4. Population finale comparaison
        ax = axes[1, 1]
        data = [without_cata['population_final'], with_cata['population_final']]
        bp = ax.boxplot(data, labels=['OFF', 'ON'], patch_artist=True)
        bp['boxes'][0].set_facecolor('lightgreen')
        bp['boxes'][1].set_facecolor('salmon')
        ax.set_xlabel('Catastrophes')
        ax.set_ylabel('Population finale')
        ax.set_title('Population avec/sans catastrophes')
        ax.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        output_path = self.plots_dir / "catastrophes_effect.png"
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close(fig)

    def plot_conservation_effect(self) -> None:
        """Effet du taux de conservation ρ."""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Effet du taux de conservation ρ', fontsize=16, fontweight='bold')

        rho_values = sorted(self.df['conservation_rate'].unique())

        # 1. θ_std par ρ
        ax = axes[0, 0]
        data_by_rho = [self.df[self.df['conservation_rate'] == rho]['theta_std']
                       for rho in rho_values]
        positions = range(len(rho_values))
        bp = ax.boxplot(data_by_rho, positions=positions, labels=[f"{r:.2f}" for r in rho_values],
                        patch_artist=True)
        for i, patch in enumerate(bp['boxes']):
            patch.set_facecolor(plt.cm.Blues(0.3 + i * 0.3))
        ax.set_xlabel('ρ (taux de conservation)')
        ax.set_ylabel('θ std (stabilité)')
        ax.set_title('Stabilité par taux de conservation')
        ax.grid(True, alpha=0.3, axis='y')

        # 2. θ_mean par ρ
        ax = axes[0, 1]
        data_by_rho = [self.df[self.df['conservation_rate'] == rho]['theta_mean']
                       for rho in rho_values]
        bp = ax.boxplot(data_by_rho, positions=positions, labels=[f"{r:.2f}" for r in rho_values],
                        patch_artist=True)
        for i, patch in enumerate(bp['boxes']):
            patch.set_facecolor(plt.cm.Reds(0.3 + i * 0.3))
        ax.axhline(1.0, color='red', linestyle='--', linewidth=1.5, label='Cible')
        ax.set_xlabel('ρ (taux de conservation)')
        ax.set_ylabel('θ moyen')
        ax.set_title('Convergence θ par ρ')
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')

        # 3. Gini par ρ
        ax = axes[1, 0]
        data_by_rho = [self.df[self.df['conservation_rate'] == rho]['gini_final']
                       for rho in rho_values]
        bp = ax.boxplot(data_by_rho, positions=positions, labels=[f"{r:.2f}" for r in rho_values],
                        patch_artist=True)
        for i, patch in enumerate(bp['boxes']):
            patch.set_facecolor(plt.cm.Purples(0.3 + i * 0.3))
        ax.set_xlabel('ρ (taux de conservation)')
        ax.set_ylabel('Gini final')
        ax.set_title('Inégalités par ρ')
        ax.grid(True, alpha=0.3, axis='y')

        # 4. Tendances (lignes moyennes)
        ax = axes[1, 1]
        theta_std_mean = [self.df[self.df['conservation_rate'] == rho]['theta_std'].mean()
                          for rho in rho_values]
        gini_mean = [self.df[self.df['conservation_rate'] == rho]['gini_final'].mean()
                     for rho in rho_values]

        ax2 = ax.twinx()
        line1 = ax.plot(rho_values, theta_std_mean, 'o-', color='steelblue',
                        linewidth=2, markersize=8, label='θ std (gauche)')
        line2 = ax2.plot(rho_values, gini_mean, 's-', color='purple',
                         linewidth=2, markersize=8, label='Gini (droite)')

        ax.set_xlabel('ρ (taux de conservation)')
        ax.set_ylabel('θ std moyen', color='steelblue')
        ax2.set_ylabel('Gini moyen', color='purple')
        ax.tick_params(axis='y', labelcolor='steelblue')
        ax2.tick_params(axis='y', labelcolor='purple')
        ax.set_title('Tendances par ρ')
        ax.grid(True, alpha=0.3)

        lines = line1 + line2
        labels = [l.get_label() for l in lines]
        ax.legend(lines, labels, loc='upper left')

        plt.tight_layout()
        output_path = self.plots_dir / "conservation_effect.png"
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close(fig)

    def plot_convergence_stability(self) -> None:
        """Convergence vs Stabilité."""
        fig, ax = plt.subplots(figsize=(12, 8))

        # Scatter coloré par Gini
        scatter = ax.scatter(self.df['theta_mean'], self.df['theta_std'],
                            c=self.df['gini_final'], s=150, cmap='RdYlGn_r',
                            alpha=0.7, edgecolor='black', linewidth=1.5)

        # Ligne θ = 1
        ax.axvline(1.0, color='red', linestyle='--', linewidth=2, alpha=0.5, label='Cible θ=1')

        # Zones de qualité
        ax.axhspan(0, 0.02, alpha=0.1, color='green', label='Excellente stabilité')
        ax.axhspan(0.02, 0.05, alpha=0.1, color='yellow')
        ax.axhspan(0.05, 1, alpha=0.1, color='red', label='Stabilité faible')

        ax.set_xlabel('θ moyen (convergence)', fontsize=12)
        ax.set_ylabel('θ std (stabilité)', fontsize=12)
        ax.set_title('Convergence vs Stabilité (couleur = Gini)', fontsize=14, fontweight='bold')

        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label('Gini final (inégalités)', fontsize=10)

        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        output_path = self.plots_dir / "convergence_stability.png"
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close(fig)

    def plot_metrics_distribution(self) -> None:
        """Distribution des métriques clés."""
        fig, axes = plt.subplots(3, 2, figsize=(14, 12))
        fig.suptitle('Distribution des métriques clés', fontsize=16, fontweight='bold')

        metrics = [
            ('theta_mean', 'θ moyen', 'steelblue'),
            ('theta_std', 'θ std', 'coral'),
            ('gini_final', 'Gini final', 'purple'),
            ('population_final', 'Population finale', 'green'),
            ('kappa_mean', 'κ moyen', 'orange'),
            ('eta_mean', 'η moyen', 'pink')
        ]

        for idx, (col, label, color) in enumerate(metrics):
            if col not in self.df.columns:
                continue

            row = idx // 2
            col_idx = idx % 2
            ax = axes[row, col_idx]

            data = self.df[col].dropna()

            # Histogramme
            ax.hist(data, bins=20, color=color, alpha=0.7, edgecolor='black')

            # Statistiques
            mean = data.mean()
            median = data.median()
            std = data.std()

            ax.axvline(mean, color='red', linestyle='--', linewidth=2, label=f'Moyenne: {mean:.3f}')
            ax.axvline(median, color='blue', linestyle=':', linewidth=2, label=f'Médiane: {median:.3f}')

            ax.set_xlabel(label)
            ax.set_ylabel('Fréquence')
            ax.set_title(f'Distribution {label}')
            ax.legend()
            ax.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        output_path = self.plots_dir / "metrics_distribution.png"
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close(fig)

    def plot_correlation_matrix(self) -> None:
        """Matrice de corrélation."""
        # Sélection colonnes numériques pertinentes
        numeric_cols = [
            'theta_mean', 'theta_std', 'gini_final',
            'population_final', 'catastrophes_total',
            'kappa_mean', 'eta_mean', 'C2_activations', 'C3_activations'
        ]

        # Filtrer colonnes existantes
        available_cols = [col for col in numeric_cols if col in self.df.columns]
        df_corr = self.df[available_cols].corr()

        fig, ax = plt.subplots(figsize=(12, 10))

        # Heatmap
        im = ax.imshow(df_corr, cmap='coolwarm', aspect='auto', vmin=-1, vmax=1)

        # Labels
        ax.set_xticks(range(len(df_corr.columns)))
        ax.set_yticks(range(len(df_corr.columns)))
        ax.set_xticklabels(df_corr.columns, rotation=45, ha='right')
        ax.set_yticklabels(df_corr.columns)

        # Valeurs dans les cellules
        for i in range(len(df_corr.columns)):
            for j in range(len(df_corr.columns)):
                value = df_corr.iloc[i, j]
                color = 'white' if abs(value) > 0.5 else 'black'
                ax.text(j, i, f'{value:.2f}', ha='center', va='center',
                       color=color, fontsize=9, fontweight='bold')

        ax.set_title('Matrice de corrélation des métriques', fontsize=14, fontweight='bold')

        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Corrélation', fontsize=10)

        plt.tight_layout()
        output_path = self.plots_dir / "correlation_matrix.png"
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close(fig)

    def plot_best_scenarios(self) -> None:
        """Comparaison des meilleurs scénarios."""
        # Top 5 scénarios par stabilité (θ_std minimal)
        top_stable = self.df.nsmallest(5, 'theta_std')

        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Top 5 scénarios les plus stables', fontsize=16, fontweight='bold')

        scenarios = top_stable['scenario_name'].tolist()
        x_pos = range(len(scenarios))

        # 1. θ_std
        ax = axes[0, 0]
        bars = ax.bar(x_pos, top_stable['theta_std'], color='steelblue', alpha=0.7, edgecolor='black')
        ax.set_xticks(x_pos)
        ax.set_xticklabels(scenarios, rotation=45, ha='right', fontsize=8)
        ax.set_ylabel('θ std')
        ax.set_title('Stabilité (θ std)')
        ax.grid(True, alpha=0.3, axis='y')

        # 2. θ_mean
        ax = axes[0, 1]
        bars = ax.bar(x_pos, top_stable['theta_mean'], color='coral', alpha=0.7, edgecolor='black')
        ax.axhline(1.0, color='red', linestyle='--', linewidth=2, label='Cible')
        ax.set_xticks(x_pos)
        ax.set_xticklabels(scenarios, rotation=45, ha='right', fontsize=8)
        ax.set_ylabel('θ moyen')
        ax.set_title('Convergence (θ moyen)')
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')

        # 3. Gini
        ax = axes[1, 0]
        bars = ax.bar(x_pos, top_stable['gini_final'], color='purple', alpha=0.7, edgecolor='black')
        ax.set_xticks(x_pos)
        ax.set_xticklabels(scenarios, rotation=45, ha='right', fontsize=8)
        ax.set_ylabel('Gini final')
        ax.set_title('Inégalités (Gini)')
        ax.grid(True, alpha=0.3, axis='y')

        # 4. Radar plot (si possible)
        ax = axes[1, 1]
        ax.axis('off')

        # Tableau de comparaison
        table_data = []
        for _, row in top_stable.iterrows():
            table_data.append([
                row['scenario_name'][:20],
                f"{row['theta_mean']:.3f}",
                f"{row['theta_std']:.4f}",
                f"{row['gini_final']:.3f}"
            ])

        table = ax.table(cellText=table_data,
                        colLabels=['Scénario', 'θ mean', 'θ std', 'Gini'],
                        cellLoc='left',
                        loc='center',
                        bbox=[0, 0, 1, 1])
        table.auto_set_font_size(False)
        table.set_fontsize(8)
        table.scale(1, 2)

        # Colorer l'en-tête
        for i in range(4):
            table[(0, i)].set_facecolor('#4CAF50')
            table[(0, i)].set_text_props(weight='bold', color='white')

        plt.tight_layout()
        output_path = self.plots_dir / "best_scenarios.png"
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close(fig)

    def plot_duration_effect(self) -> None:
        """Effet de la durée de simulation."""
        if 'steps' not in self.df.columns:
            return

        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Effet de la durée de simulation', fontsize=16, fontweight='bold')

        steps_values = sorted(self.df['steps'].unique())

        # Boxplots pour chaque métrique
        metrics = [
            ('theta_std', 'θ std', axes[0, 0], 'lightblue'),
            ('theta_mean', 'θ moyen', axes[0, 1], 'lightcoral'),
            ('gini_final', 'Gini final', axes[1, 0], 'mediumpurple'),
            ('population_final', 'Population finale', axes[1, 1], 'lightgreen')
        ]

        for col, label, ax, color in metrics:
            data_by_steps = [self.df[self.df['steps'] == s][col] for s in steps_values]
            positions = range(len(steps_values))
            bp = ax.boxplot(data_by_steps, positions=positions,
                           labels=[str(s) for s in steps_values],
                           patch_artist=True)
            for patch in bp['boxes']:
                patch.set_facecolor(color)

            if col == 'theta_mean':
                ax.axhline(1.0, color='red', linestyle='--', linewidth=1.5, label='Cible')
                ax.legend()

            ax.set_xlabel('Durée (cycles)')
            ax.set_ylabel(label)
            ax.set_title(f'{label} par durée')
            ax.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        output_path = self.plots_dir / "duration_effect.png"
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close(fig)

    def plot_heatmaps(self) -> None:
        """Heatmaps 2D pour explorer l'espace des paramètres."""
        if 'initial_agents' not in self.df.columns or 'conservation_rate' not in self.df.columns:
            return

        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        fig.suptitle('Heatmaps 2D - Exploration paramétrique', fontsize=16, fontweight='bold')

        # Moyenne par combinaison (population, conservation_rate)
        pivot_theta = self.df.pivot_table(
            values='theta_std',
            index='initial_agents',
            columns='conservation_rate',
            aggfunc='mean'
        )

        pivot_gini = self.df.pivot_table(
            values='gini_final',
            index='initial_agents',
            columns='conservation_rate',
            aggfunc='mean'
        )

        # Heatmap 1: θ_std
        ax = axes[0]
        im1 = ax.imshow(pivot_theta, cmap='YlOrRd', aspect='auto')
        ax.set_xticks(range(len(pivot_theta.columns)))
        ax.set_yticks(range(len(pivot_theta.index)))
        ax.set_xticklabels([f"{x:.2f}" for x in pivot_theta.columns])
        ax.set_yticklabels(pivot_theta.index)
        ax.set_xlabel('ρ (conservation)')
        ax.set_ylabel('Population initiale')
        ax.set_title('θ std (stabilité)')

        for i in range(len(pivot_theta.index)):
            for j in range(len(pivot_theta.columns)):
                value = pivot_theta.iloc[i, j]
                if not np.isnan(value):
                    ax.text(j, i, f'{value:.4f}', ha='center', va='center',
                           color='white' if value > pivot_theta.mean().mean() else 'black',
                           fontsize=9, fontweight='bold')

        plt.colorbar(im1, ax=ax, label='θ std')

        # Heatmap 2: Gini
        ax = axes[1]
        im2 = ax.imshow(pivot_gini, cmap='RdYlGn_r', aspect='auto')
        ax.set_xticks(range(len(pivot_gini.columns)))
        ax.set_yticks(range(len(pivot_gini.index)))
        ax.set_xticklabels([f"{x:.2f}" for x in pivot_gini.columns])
        ax.set_yticklabels(pivot_gini.index)
        ax.set_xlabel('ρ (conservation)')
        ax.set_ylabel('Population initiale')
        ax.set_title('Gini final (inégalités)')

        for i in range(len(pivot_gini.index)):
            for j in range(len(pivot_gini.columns)):
                value = pivot_gini.iloc[i, j]
                if not np.isnan(value):
                    ax.text(j, i, f'{value:.3f}', ha='center', va='center',
                           color='white' if value > pivot_gini.mean().mean() else 'black',
                           fontsize=9, fontweight='bold')

        plt.colorbar(im2, ax=ax, label='Gini')

        plt.tight_layout()
        output_path = self.plots_dir / "heatmaps.png"
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close(fig)


def main():
    """Point d'entrée principal."""
    if len(sys.argv) < 2:
        print("Usage: python -m iris.simulations.plot_analysis <results_dir>")
        print("Exemple: python -m iris.simulations.plot_analysis results/test_grid")
        sys.exit(1)

    results_dir = Path(sys.argv[1])

    if not results_dir.exists():
        print(f"❌ Répertoire introuvable: {results_dir}")
        sys.exit(1)

    # Création de l'analyseur et génération des graphiques
    try:
        analyzer = IRISPlotAnalysis(results_dir)
        analyzer.plot_all()

        print(f"\n✅ Analyse graphique terminée!")
        print(f"📁 Graphiques disponibles dans: {analyzer.plots_dir}")

    except Exception as e:
        print(f"❌ Erreur lors de l'analyse: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
