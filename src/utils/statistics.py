"""Reusable statistical helpers for modality-level summaries and tests."""

from __future__ import annotations

from typing import Iterable

import numpy as np
import pandas as pd
from scipy.stats import kruskal, mannwhitneyu


def descriptive_statistics(values: pd.Series) -> dict[str, float]:
    """Return descriptive statistics used across all project summaries."""
    clean_values = values.dropna().astype(float)
    q1 = clean_values.quantile(0.25)
    q3 = clean_values.quantile(0.75)
    mean_value = clean_values.mean()
    std_value = clean_values.std(ddof=1)

    coefficient_of_variation = np.nan
    if not np.isclose(mean_value, 0.0):
        coefficient_of_variation = std_value / mean_value

    return {
        "count": int(clean_values.count()),
        "mean": float(mean_value),
        "std": float(std_value),
        "median": float(clean_values.median()),
        "min": float(clean_values.min()),
        "max": float(clean_values.max()),
        "Q1": float(q1),
        "Q3": float(q3),
        "IQR": float(q3 - q1),
        "coefficient_of_variation": float(coefficient_of_variation),
    }


def summarize_by_modality(
    dataframe: pd.DataFrame,
    metrics: Iterable[str],
    modality_column: str = "modality",
) -> pd.DataFrame:
    """Create a tidy summary table by modality and metric."""
    rows: list[dict[str, float | str]] = []

    for modality, group in dataframe.groupby(modality_column, sort=True):
        for metric in metrics:
            stats = descriptive_statistics(group[metric])
            rows.append({"modality": modality, "metric": metric, **stats})

    return pd.DataFrame(rows)


def kruskal_wallis_by_metric(
    dataframe: pd.DataFrame,
    metrics: Iterable[str],
    dataset_name: str,
    modality_column: str = "modality",
) -> pd.DataFrame:
    """Run a Kruskal-Wallis test for each metric across modalities."""
    rows: list[dict[str, float | str | int]] = []

    for metric in metrics:
        samples = [
            group[metric].dropna().astype(float).to_numpy()
            for _, group in dataframe.groupby(modality_column, sort=True)
        ]

        if len(samples) < 2 or any(len(sample) == 0 for sample in samples):
            statistic = np.nan
            p_value = np.nan
        else:
            statistic, p_value = kruskal(*samples)

        rows.append(
            {
                "dataset": dataset_name,
                "test": "Kruskal-Wallis",
                "metric": metric,
                "comparison": "all_modalities",
                "statistic": float(statistic),
                "p_value": float(p_value),
                "n_groups": len(samples),
            }
        )

    return pd.DataFrame(rows)


def mann_whitney_against_reference(
    dataframe: pd.DataFrame,
    metrics: Iterable[str],
    reference_modality: str,
    dataset_name: str,
    modality_column: str = "modality",
) -> pd.DataFrame:
    """Compare one reference modality against each other modality."""
    rows: list[dict[str, float | str | int]] = []
    modalities = sorted(dataframe[modality_column].unique())

    for metric in metrics:
        reference_values = dataframe.loc[
            dataframe[modality_column] == reference_modality, metric
        ].dropna()

        for modality in modalities:
            if modality == reference_modality:
                continue

            comparison_values = dataframe.loc[
                dataframe[modality_column] == modality, metric
            ].dropna()

            if len(reference_values) == 0 or len(comparison_values) == 0:
                statistic = np.nan
                p_value = np.nan
            else:
                statistic, p_value = mannwhitneyu(
                    reference_values,
                    comparison_values,
                    alternative="two-sided",
                )

            rows.append(
                {
                    "dataset": dataset_name,
                    "test": "Mann-Whitney U",
                    "metric": metric,
                    "comparison": f"{reference_modality}_vs_{modality}",
                    "statistic": float(statistic),
                    "p_value": float(p_value),
                    "n_groups": 2,
                }
            )

    return pd.DataFrame(rows)

