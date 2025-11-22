"""
IRIS Experiment Report Generator
=================================

Génère un rapport d'analyse à partir des résultats d'expériences.

Usage:
    python -m iris.simulations.generate_report results/test_grid
"""

import sys
from pathlib import Path
from typing import Optional
from datetime import datetime

import pandas as pd
import numpy as np


def generate_markdown_report(summary_path: Path, output_path: Optional[Path] = None) -> str:
    """
    Génère un rapport Markdown à partir du fichier summary.csv.

    Args:
        summary_path: Chemin vers summary.csv
        output_path: Chemin de sortie (optionnel, par défaut: rapport.md à côté du summary)

    Returns:
        Contenu du rapport en Markdown
    """
    # Lecture du summary
    df = pd.read_csv(summary_path)

    # Chemin de sortie par défaut
    if output_path is None:
        output_path = summary_path.parent / "RAPPORT_ANALYSE.md"

    # Construction du rapport
    report_lines = []

    # En-tête
    report_lines.append("# IRIS - Rapport d'Analyse des Expériences")
    report_lines.append("")
    report_lines.append(f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append(f"**Nombre d'expériences**: {len(df)}")
    report_lines.append(f"**Source**: `{summary_path}`")
    report_lines.append("")
    report_lines.append("---")
    report_lines.append("")

    # 1. Résumé global
    report_lines.append("## 1. Résumé Global")
    report_lines.append("")
    report_lines.append("### 1.1 Statistiques générales")
    report_lines.append("")
    report_lines.append("| Métrique | Moyenne | Écart-type | Min | Max |")
    report_lines.append("|----------|---------|------------|-----|-----|")

    metrics = {
        'θ (theta) moyen': 'theta_mean',
        'θ écart-type': 'theta_std',
        'Gini final': 'gini_final',
        'Population finale': 'population_final',
        'Catastrophes totales': 'catastrophes_total'
    }

    for label, col in metrics.items():
        if col in df.columns:
            mean = df[col].mean()
            std = df[col].std()
            min_val = df[col].min()
            max_val = df[col].max()
            report_lines.append(f"| {label} | {mean:.4f} | {std:.4f} | {min_val:.4f} | {max_val:.4f} |")

    report_lines.append("")

    # 2. Convergence de θ
    report_lines.append("## 2. Analyse de la Convergence θ")
    report_lines.append("")
    report_lines.append("### 2.1 Stabilité du thermomètre")
    report_lines.append("")

    # Scénarios les plus stables (θ_std faible)
    df_sorted_stable = df.nsmallest(5, 'theta_std')
    report_lines.append("**Scénarios les plus stables** (θ_std faible):")
    report_lines.append("")
    report_lines.append("| Scénario | θ moyen | θ std | θ final |")
    report_lines.append("|----------|---------|-------|---------|")
    for _, row in df_sorted_stable.iterrows():
        report_lines.append(f"| `{row['scenario_name']}` | {row['theta_mean']:.4f} | "
                          f"{row['theta_std']:.4f} | {row['theta_final']:.4f} |")
    report_lines.append("")

    # Scénarios les moins stables
    df_sorted_unstable = df.nlargest(5, 'theta_std')
    report_lines.append("**Scénarios les moins stables** (θ_std élevé):")
    report_lines.append("")
    report_lines.append("| Scénario | θ moyen | θ std | θ final |")
    report_lines.append("|----------|---------|-------|---------|")
    for _, row in df_sorted_unstable.iterrows():
        report_lines.append(f"| `{row['scenario_name']}` | {row['theta_mean']:.4f} | "
                          f"{row['theta_std']:.4f} | {row['theta_final']:.4f} |")
    report_lines.append("")

    # 3. Effet des paramètres
    report_lines.append("## 3. Effet des Paramètres")
    report_lines.append("")

    # 3.1 Catastrophes ON/OFF
    if 'enable_catastrophes' in df.columns:
        report_lines.append("### 3.1 Impact des catastrophes")
        report_lines.append("")

        with_cata = df[df['enable_catastrophes'] == True]
        without_cata = df[df['enable_catastrophes'] == False]

        report_lines.append("| Paramètre | Catastrophes ON | Catastrophes OFF | Différence |")
        report_lines.append("|-----------|-----------------|------------------|------------|")

        if len(with_cata) > 0 and len(without_cata) > 0:
            params_to_compare = [
                ('θ std', 'theta_std'),
                ('θ moyen', 'theta_mean'),
                ('Gini final', 'gini_final'),
                ('Population finale', 'population_final')
            ]

            for label, col in params_to_compare:
                on_val = with_cata[col].mean()
                off_val = without_cata[col].mean()
                diff = on_val - off_val
                diff_pct = (diff / off_val * 100) if off_val != 0 else 0
                report_lines.append(f"| {label} | {on_val:.4f} | {off_val:.4f} | "
                                  f"{diff:+.4f} ({diff_pct:+.1f}%) |")

        report_lines.append("")
        report_lines.append(f"**Observations**:")
        report_lines.append(f"- Scénarios avec catastrophes: {len(with_cata)}")
        report_lines.append(f"- Scénarios sans catastrophes: {len(without_cata)}")
        if len(with_cata) > 0:
            report_lines.append(f"- Total catastrophes (scénarios ON): {with_cata['catastrophes_total'].sum()}")
        report_lines.append("")

    # 3.2 Taux de conservation ρ
    if 'conservation_rate' in df.columns:
        report_lines.append("### 3.2 Impact du taux de conservation ρ")
        report_lines.append("")

        rho_values = sorted(df['conservation_rate'].unique())

        report_lines.append("| ρ | θ std | θ moyen | Gini final | Pop finale |")
        report_lines.append("|---|-------|---------|------------|------------|")

        for rho in rho_values:
            subset = df[df['conservation_rate'] == rho]
            report_lines.append(f"| {rho:.2f} | {subset['theta_std'].mean():.4f} | "
                              f"{subset['theta_mean'].mean():.4f} | "
                              f"{subset['gini_final'].mean():.4f} | "
                              f"{subset['population_final'].mean():.0f} |")

        report_lines.append("")
        report_lines.append("**Interprétation**:")
        report_lines.append("- ρ = 0.0 : RU maximum (100% de V disponible)")
        report_lines.append("- ρ = 0.05 : RU standard (95% de V disponible)")
        report_lines.append("- ρ = 0.15 : RU réduit (85% de V disponible)")
        report_lines.append("")

    # 3.3 Taille de la population initiale
    if 'initial_agents' in df.columns:
        report_lines.append("### 3.3 Impact de la population initiale")
        report_lines.append("")

        pop_values = sorted(df['initial_agents'].unique())

        report_lines.append("| Pop. initiale | θ std | θ moyen | Gini final | Pop finale moyenne |")
        report_lines.append("|---------------|-------|---------|------------|--------------------|")

        for pop in pop_values:
            subset = df[df['initial_agents'] == pop]
            report_lines.append(f"| {pop} | {subset['theta_std'].mean():.4f} | "
                              f"{subset['theta_mean'].mean():.4f} | "
                              f"{subset['gini_final'].mean():.4f} | "
                              f"{subset['population_final'].mean():.0f} |")

        report_lines.append("")

    # 4. Inégalités (Gini)
    report_lines.append("## 4. Analyse des Inégalités (Gini)")
    report_lines.append("")

    # Scénarios les plus égalitaires
    df_sorted_gini_low = df.nsmallest(5, 'gini_final')
    report_lines.append("**Scénarios les plus égalitaires** (Gini faible):")
    report_lines.append("")
    report_lines.append("| Scénario | Gini final | θ moyen | Pop. finale |")
    report_lines.append("|----------|-----------|---------|-------------|")
    for _, row in df_sorted_gini_low.iterrows():
        report_lines.append(f"| `{row['scenario_name']}` | {row['gini_final']:.4f} | "
                          f"{row['theta_mean']:.4f} | {row['population_final']:.0f} |")
    report_lines.append("")

    # Scénarios les plus inégalitaires
    df_sorted_gini_high = df.nlargest(5, 'gini_final')
    report_lines.append("**Scénarios les plus inégalitaires** (Gini élevé):")
    report_lines.append("")
    report_lines.append("| Scénario | Gini final | θ moyen | Pop. finale |")
    report_lines.append("|----------|-----------|---------|-------------|")
    for _, row in df_sorted_gini_high.iterrows():
        report_lines.append(f"| `{row['scenario_name']}` | {row['gini_final']:.4f} | "
                          f"{row['theta_mean']:.4f} | {row['population_final']:.0f} |")
    report_lines.append("")

    # 5. Régulation (C2/C3)
    report_lines.append("## 5. Activations de Régulation (C2/C3)")
    report_lines.append("")

    if 'C2_activations' in df.columns and 'C3_activations' in df.columns:
        total_C2 = df['C2_activations'].sum()
        total_C3 = df['C3_activations'].sum()

        report_lines.append(f"- **Total activations C2** (régulation profonde): {total_C2}")
        report_lines.append(f"- **Total activations C3** (urgence): {total_C3}")
        report_lines.append("")

        if total_C3 > 0:
            # Scénarios ayant déclenché C3
            df_with_C3 = df[df['C3_activations'] > 0]
            report_lines.append(f"**Scénarios ayant déclenché C3** ({len(df_with_C3)} scénarios):")
            report_lines.append("")
            report_lines.append("| Scénario | C3 activations | θ std | θ moyen |")
            report_lines.append("|----------|----------------|-------|---------|")
            for _, row in df_with_C3.iterrows():
                report_lines.append(f"| `{row['scenario_name']}` | {row['C3_activations']} | "
                                  f"{row['theta_std']:.4f} | {row['theta_mean']:.4f} |")
            report_lines.append("")
        else:
            report_lines.append("✅ **Aucun scénario n'a déclenché C3** - Système stable")
            report_lines.append("")

    # 6. Performance
    if 'elapsed_time_s' in df.columns:
        report_lines.append("## 6. Performance des Simulations")
        report_lines.append("")

        total_time = df['elapsed_time_s'].sum()
        mean_time = df['elapsed_time_s'].mean()

        report_lines.append(f"- **Temps total**: {total_time:.1f}s ({total_time/60:.1f} min)")
        report_lines.append(f"- **Temps moyen par simulation**: {mean_time:.2f}s")
        report_lines.append(f"- **Temps le plus rapide**: {df['elapsed_time_s'].min():.2f}s")
        report_lines.append(f"- **Temps le plus long**: {df['elapsed_time_s'].max():.2f}s")
        report_lines.append("")

    # 7. Conclusions
    report_lines.append("## 7. Conclusions et Recommandations")
    report_lines.append("")

    # Convergence θ
    mean_theta_std = df['theta_std'].mean()
    mean_theta_mean = df['theta_mean'].mean()
    theta_deviation = abs(mean_theta_mean - 1.0)

    report_lines.append("### 7.1 Convergence du thermomètre")
    if theta_deviation < 0.1:
        report_lines.append(f"✅ **Excellente convergence**: θ moyen = {mean_theta_mean:.4f} (écart: {theta_deviation:.4f})")
    elif theta_deviation < 0.3:
        report_lines.append(f"✓ **Bonne convergence**: θ moyen = {mean_theta_mean:.4f} (écart: {theta_deviation:.4f})")
    else:
        report_lines.append(f"⚠ **Convergence à améliorer**: θ moyen = {mean_theta_mean:.4f} (écart: {theta_deviation:.4f})")

    if mean_theta_std < 0.02:
        report_lines.append(f"✅ **Excellente stabilité**: θ std moyen = {mean_theta_std:.4f}")
    elif mean_theta_std < 0.05:
        report_lines.append(f"✓ **Bonne stabilité**: θ std moyen = {mean_theta_std:.4f}")
    else:
        report_lines.append(f"⚠ **Stabilité à améliorer**: θ std moyen = {mean_theta_std:.4f}")

    report_lines.append("")

    # Inégalités
    mean_gini = df['gini_final'].mean()
    report_lines.append("### 7.2 Inégalités de richesse")
    if mean_gini < 0.4:
        report_lines.append(f"✅ **Faible inégalité**: Gini moyen = {mean_gini:.4f}")
    elif mean_gini < 0.6:
        report_lines.append(f"✓ **Inégalité modérée**: Gini moyen = {mean_gini:.4f}")
    else:
        report_lines.append(f"⚠ **Forte inégalité**: Gini moyen = {mean_gini:.4f}")

    report_lines.append("")

    # Recommandations
    report_lines.append("### 7.3 Recommandations")
    report_lines.append("")

    # Meilleure configuration
    best_idx = df['theta_std'].idxmin()  # Configuration la plus stable
    best_row = df.loc[best_idx]

    report_lines.append(f"**Configuration recommandée** (stabilité optimale):")
    report_lines.append(f"- Scénario: `{best_row['scenario_name']}`")
    report_lines.append(f"- Population initiale: {best_row['initial_agents']}")
    report_lines.append(f"- Catastrophes: {'ON' if best_row['enable_catastrophes'] else 'OFF'}")
    report_lines.append(f"- ρ (conservation): {best_row['conservation_rate']}")
    report_lines.append(f"- Résultats: θ={best_row['theta_mean']:.4f} ± {best_row['theta_std']:.4f}, "
                      f"Gini={best_row['gini_final']:.4f}")
    report_lines.append("")

    # Footer
    report_lines.append("---")
    report_lines.append("")
    report_lines.append("*Rapport généré automatiquement par `iris.simulations.generate_report`*")
    report_lines.append("")

    # Assemblage du rapport
    report_content = "\n".join(report_lines)

    # Sauvegarde
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report_content)

    print(f"✅ Rapport généré: {output_path}")

    return report_content


def main():
    """Point d'entrée principal."""
    if len(sys.argv) < 2:
        print("Usage: python -m iris.simulations.generate_report <results_dir>")
        print("Exemple: python -m iris.simulations.generate_report results/test_grid")
        sys.exit(1)

    results_dir = Path(sys.argv[1])
    summary_path = results_dir / "summary.csv"

    if not summary_path.exists():
        print(f"❌ Fichier summary.csv introuvable: {summary_path}")
        sys.exit(1)

    print(f"📊 Génération du rapport d'analyse...")
    print(f"   Source: {summary_path}")

    report_content = generate_markdown_report(summary_path)

    print(f"\n{'='*80}")
    print(f"✅ Rapport d'analyse généré avec succès")
    print(f"{'='*80}")


if __name__ == "__main__":
    main()
