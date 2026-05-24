"""
Generate presentation-ready figures for the 3D interaction analysis.

Inputs:
    data/processed/quantitative_metrics.csv
    data/processed/qualitative_scores.csv

Outputs:
    figures/01_boxplot_translation_error.png
    figures/02_boxplot_rotation_error.png
    figures/03_boxplot_completion_time.png
    figures/04_boxplot_path_length.png
    figures/06_qualitative_scores_by_modality.png
    figures/07_preference_votes.png
    figures/08_summary_radar_optional.png

Usage:
    python src/04_plot_results.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
FIGURES_DIR = PROJECT_ROOT / "figures"

QUANTITATIVE_INPUT_PATH = PROCESSED_DIR / "quantitative_metrics.csv"
QUALITATIVE_INPUT_PATH = PROCESSED_DIR / "qualitative_scores.csv"

QUANTITATIVE_ORDER = ["SpaceMouse", "Mouse2D", "Trackpad"]
QUALITATIVE_ORDER = ["SpaceMouse", "Mouse2D", "Trackpad", "HandGrab"]

PALETTE = {
    "SpaceMouse": "#2A9D8F",
    "Mouse2D": "#E76F51",
    "Trackpad": "#457B9D",
    "HandGrab": "#F4A261",
}

BOXPLOT_CONFIG = [
    (
        "translation_error_mm",
        "Erreur de translation par modalite",
        "Erreur de translation (mm)",
        "01_boxplot_translation_error.png",
    ),
    (
        "rotation_error_deg",
        "Erreur de rotation par modalite",
        "Erreur de rotation (deg)",
        "02_boxplot_rotation_error.png",
    ),
    (
        "completion_time_s",
        "Temps de realisation par modalite",
        "Temps de realisation (s)",
        "03_boxplot_completion_time.png",
    ),
    (
        "path_length_mm",
        "Longueur de chemin par modalite",
        "Longueur de chemin (mm)",
        "04_boxplot_path_length.png",
    ),
]

QUALITATIVE_LABELS = {
    "intuitiveness_score": "Intuitivite",
    "perceived_precision_score": "Precision percue",
    "physical_discomfort_score": "Inconfort physique",
    "surgical_relevance_score": "Pertinence chirurgicale",
}


def configure_plot_style() -> None:
    """Apply one consistent visual style across all figures."""
    sns.set_theme(style="whitegrid", context="notebook", font_scale=1.2)
    plt.rcParams["figure.dpi"] = 120
    plt.rcParams["savefig.dpi"] = 200
    plt.rcParams["axes.titleweight"] = "bold"


def validate_inputs() -> None:
    """Ensure plotting inputs have already been generated."""
    missing_paths = [
        path
        for path in [QUANTITATIVE_INPUT_PATH, QUALITATIVE_INPUT_PATH]
        if not path.exists()
    ]

    if missing_paths:
        missing = "\n".join(str(path) for path in missing_paths)
        raise FileNotFoundError(
            "Missing input file(s):\n"
            f"{missing}\n"
            "Run scripts 01, 02 and 03 before plotting."
        )


def save_current_figure(output_name: str) -> None:
    """Save the active matplotlib figure and close it cleanly."""
    output_path = FIGURES_DIR / output_name
    plt.tight_layout()
    plt.savefig(output_path, bbox_inches="tight")
    plt.close()
    print(f"Saved figure: {output_path}")


def plot_quantitative_boxplot(
    dataframe: pd.DataFrame,
    metric: str,
    title: str,
    y_label: str,
    output_name: str,
) -> None:
    """Create a boxplot with individual trial points for one quantitative metric."""
    plt.figure(figsize=(10, 6))
    sns.boxplot(
        data=dataframe,
        x="modality",
        y=metric,
        hue="modality",
        order=QUANTITATIVE_ORDER,
        palette=PALETTE,
        showfliers=False,
        legend=False,
    )
    sns.stripplot(
        data=dataframe,
        x="modality",
        y=metric,
        order=QUANTITATIVE_ORDER,
        color="#1F2933",
        size=4,
        alpha=0.45,
        jitter=0.22,
    )
    plt.title(title)
    plt.xlabel("Modalite")
    plt.ylabel(y_label)
    save_current_figure(output_name)


def plot_qualitative_scores(qualitative_scores: pd.DataFrame) -> None:
    """Plot mean questionnaire scores by modality and question."""
    score_columns = list(QUALITATIVE_LABELS.keys())
    long_scores = qualitative_scores.melt(
        id_vars=["participant_id", "modality"],
        value_vars=score_columns,
        var_name="score_type",
        value_name="score",
    )
    long_scores["score_type"] = long_scores["score_type"].map(QUALITATIVE_LABELS)

    plt.figure(figsize=(13, 7))
    sns.barplot(
        data=long_scores,
        x="modality",
        y="score",
        hue="score_type",
        order=QUALITATIVE_ORDER,
        palette="Set2",
        errorbar="sd",
    )
    plt.title("Scores qualitatifs moyens par modalite")
    plt.xlabel("")
    plt.ylabel("Score moyen (1 a 5)")
    plt.ylim(0, 5)
    plt.legend(title="Critere", loc="upper center", bbox_to_anchor=(0.5, -0.08), ncol=4)
    save_current_figure("06_qualitative_scores_by_modality.png")


def plot_preference_votes(qualitative_scores: pd.DataFrame) -> None:
    """Plot one final preference vote per participant."""
    preference_votes = (
        qualitative_scores[["participant_id", "preferred_modality"]]
        .drop_duplicates()
        .value_counts("preferred_modality")
        .reindex(QUALITATIVE_ORDER, fill_value=0)
        .reset_index()
    )
    preference_votes.columns = ["preferred_modality", "votes"]

    plt.figure(figsize=(9, 6))
    sns.barplot(
        data=preference_votes,
        x="preferred_modality",
        y="votes",
        hue="preferred_modality",
        order=QUALITATIVE_ORDER,
        palette=PALETTE,
        legend=False,
    )
    plt.title("Votes de preference finale")
    plt.xlabel("Modalite preferee")
    plt.ylabel("Nombre de participants")
    plt.ylim(0, max(preference_votes["votes"].max() + 1, 5))

    for index, row in preference_votes.iterrows():
        plt.text(index, row["votes"] + 0.1, int(row["votes"]), ha="center")

    save_current_figure("07_preference_votes.png")


def normalize_lower_is_better(dataframe: pd.DataFrame, metrics: list[str]) -> pd.DataFrame:
    """Convert lower-is-better metrics to 0-1 scores where higher means better."""
    means = dataframe.groupby("modality")[metrics].mean().reindex(QUANTITATIVE_ORDER)
    normalized = pd.DataFrame(index=means.index)

    for metric in metrics:
        min_value = means[metric].min()
        max_value = means[metric].max()

        if np.isclose(max_value, min_value):
            normalized[metric] = 1.0
        else:
            normalized[metric] = 1.0 - (means[metric] - min_value) / (max_value - min_value)

    return normalized


def plot_summary_radar(quantitative_metrics: pd.DataFrame) -> None:
    """Create an optional radar chart summarizing relative quantitative performance."""
    metrics = [
        "translation_error_mm",
        "rotation_error_deg",
        "completion_time_s",
        "path_length_mm",
        "nb_corrections",
    ]
    metric_labels = [
        "Translation",
        "Rotation",
        "Temps",
        "Chemin",
        "Corrections",
    ]
    normalized = normalize_lower_is_better(quantitative_metrics, metrics)

    angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw={"polar": True})

    for modality in QUANTITATIVE_ORDER:
        values = normalized.loc[modality, metrics].tolist()
        values += values[:1]
        ax.plot(angles, values, label=modality, linewidth=2.5, color=PALETTE[modality])
        ax.fill(angles, values, alpha=0.10, color=PALETTE[modality])

    ax.set_title("Performance quantitative relative", pad=24, fontweight="bold")
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(metric_labels)
    ax.set_yticks([0.25, 0.5, 0.75, 1.0])
    ax.set_ylim(0, 1)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.08), ncol=3)

    save_current_figure("08_summary_radar_optional.png")


def main() -> None:
    """Generate all expected figures."""
    validate_inputs()
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    configure_plot_style()

    quantitative_metrics = pd.read_csv(QUANTITATIVE_INPUT_PATH)
    qualitative_scores = pd.read_csv(QUALITATIVE_INPUT_PATH)

    for metric, title, y_label, output_name in BOXPLOT_CONFIG:
        plot_quantitative_boxplot(
            quantitative_metrics,
            metric=metric,
            title=title,
            y_label=y_label,
            output_name=output_name,
        )

    plot_qualitative_scores(qualitative_scores)
    plot_preference_votes(qualitative_scores)
    plot_summary_radar(quantitative_metrics)


if __name__ == "__main__":
    main()
