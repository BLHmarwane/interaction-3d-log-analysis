"""
Compute quantitative metrics from serialized 4x4 transformation matrices.

Inputs:
    data/raw/synthetic_transform_logs.csv

Outputs:
    data/processed/quantitative_metrics.csv

Usage:
    python src/02_compute_metrics_from_transforms.py
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from utils.transformations import (
    compute_relative_transform,
    compute_rotation_error,
    compute_translation_error,
    matrix_from_json,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "synthetic_transform_logs.csv"
METRICS_OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "quantitative_metrics.csv"

OUTPUT_COLUMNS = [
    "participant_id",
    "scene_id",
    "trial_id",
    "modality",
    "translation_error_mm",
    "rotation_error_deg",
    "completion_time_s",
    "path_length_mm",
    "nb_corrections",
    "success",
]


def compute_metrics_for_row(row: pd.Series) -> dict[str, object]:
    """Compute translation and rotation errors for one trial row."""
    target_matrix = matrix_from_json(row["target_matrix"])
    final_matrix = matrix_from_json(row["final_matrix"])
    transform_error = compute_relative_transform(target_matrix, final_matrix)

    return {
        "participant_id": row["participant_id"],
        "scene_id": row["scene_id"],
        "trial_id": row["trial_id"],
        "modality": row["modality"],
        "translation_error_mm": round(compute_translation_error(transform_error), 6),
        "rotation_error_deg": round(compute_rotation_error(transform_error), 6),
        "completion_time_s": row["completion_time_s"],
        "path_length_mm": row["path_length_mm"],
        "nb_corrections": row["nb_corrections"],
        "success": row["success"],
    }


def compute_metrics(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Compute clean quantitative metrics from the raw transform log table."""
    metric_rows = [compute_metrics_for_row(row) for _, row in dataframe.iterrows()]
    return pd.DataFrame(metric_rows, columns=OUTPUT_COLUMNS)


def main() -> None:
    """Load raw logs, compute matrix-derived metrics and export them."""
    if not RAW_DATA_PATH.exists():
        raise FileNotFoundError(
            f"Missing input file: {RAW_DATA_PATH}. "
            "Run python src/01_generate_synthetic_data.py first."
        )

    raw_logs = pd.read_csv(RAW_DATA_PATH)
    metrics = compute_metrics(raw_logs)

    METRICS_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    metrics.to_csv(METRICS_OUTPUT_PATH, index=False)

    print(f"Computed metrics: {METRICS_OUTPUT_PATH}")
    print(f"Rows exported: {len(metrics)}")


if __name__ == "__main__":
    main()

