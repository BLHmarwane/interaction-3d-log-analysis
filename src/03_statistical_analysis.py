"""
Run descriptive and non-parametric statistical analysis by modality.

Inputs:
    data/processed/quantitative_metrics.csv
    data/processed/qualitative_scores.csv

Outputs:
    data/processed/summary_quantitative_by_modality.csv
    data/processed/summary_qualitative_by_modality.csv
    data/processed/statistical_tests.csv

Usage:
    python src/03_statistical_analysis.py
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from utils.statistics import (
    kruskal_wallis_by_metric,
    mann_whitney_against_reference,
    summarize_by_modality,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

QUANTITATIVE_INPUT_PATH = PROCESSED_DIR / "quantitative_metrics.csv"
QUALITATIVE_INPUT_PATH = PROCESSED_DIR / "qualitative_scores.csv"
QUANTITATIVE_SUMMARY_PATH = PROCESSED_DIR / "summary_quantitative_by_modality.csv"
QUALITATIVE_SUMMARY_PATH = PROCESSED_DIR / "summary_qualitative_by_modality.csv"
TESTS_OUTPUT_PATH = PROCESSED_DIR / "statistical_tests.csv"

QUANTITATIVE_METRICS = [
    "translation_error_mm",
    "rotation_error_deg",
    "completion_time_s",
    "path_length_mm",
    "nb_corrections",
]

QUALITATIVE_METRICS = [
    "intuitiveness_score",
    "perceived_precision_score",
    "physical_discomfort_score",
    "surgical_relevance_score",
]


def validate_inputs() -> None:
    """Fail early with a clear message when required inputs are missing."""
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
            "Run scripts 01 and 02 before statistical analysis."
        )


def run_statistical_tests(
    quantitative_metrics: pd.DataFrame,
    qualitative_scores: pd.DataFrame,
) -> pd.DataFrame:
    """Run global and post-hoc tests without mixing quantitative and qualitative data."""
    test_tables = [
        kruskal_wallis_by_metric(
            quantitative_metrics,
            QUANTITATIVE_METRICS,
            dataset_name="quantitative",
        ),
        mann_whitney_against_reference(
            quantitative_metrics,
            QUANTITATIVE_METRICS,
            reference_modality="SpaceMouse",
            dataset_name="quantitative",
        ),
        kruskal_wallis_by_metric(
            qualitative_scores,
            QUALITATIVE_METRICS,
            dataset_name="qualitative",
        ),
        mann_whitney_against_reference(
            qualitative_scores,
            QUALITATIVE_METRICS,
            reference_modality="SpaceMouse",
            dataset_name="qualitative",
        ),
    ]

    return pd.concat(test_tables, ignore_index=True)


def main() -> None:
    """Create summary tables and statistical test exports."""
    validate_inputs()

    quantitative_metrics = pd.read_csv(QUANTITATIVE_INPUT_PATH)
    qualitative_scores = pd.read_csv(QUALITATIVE_INPUT_PATH)

    quantitative_summary = summarize_by_modality(
        quantitative_metrics,
        QUANTITATIVE_METRICS,
    )
    qualitative_summary = summarize_by_modality(
        qualitative_scores,
        QUALITATIVE_METRICS,
    )
    statistical_tests = run_statistical_tests(quantitative_metrics, qualitative_scores)

    quantitative_summary.to_csv(QUANTITATIVE_SUMMARY_PATH, index=False)
    qualitative_summary.to_csv(QUALITATIVE_SUMMARY_PATH, index=False)
    statistical_tests.to_csv(TESTS_OUTPUT_PATH, index=False)

    print(f"Quantitative summary: {QUANTITATIVE_SUMMARY_PATH}")
    print(f"Qualitative summary: {QUALITATIVE_SUMMARY_PATH}")
    print(f"Statistical tests: {TESTS_OUTPUT_PATH}")


if __name__ == "__main__":
    main()

