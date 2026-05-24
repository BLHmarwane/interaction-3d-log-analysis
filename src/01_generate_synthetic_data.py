"""
Generate representative synthetic datasets for 3D interaction modality analysis.

Inputs:
    None.

Outputs:
    data/raw/synthetic_transform_logs.csv
    data/processed/qualitative_scores.csv

Usage:
    python src/01_generate_synthetic_data.py
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from utils.transformations import create_transform_matrix, matrix_to_json


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "synthetic_transform_logs.csv"
QUALITATIVE_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "qualitative_scores.csv"
RANDOM_SEED = 42

PARTICIPANTS = [f"P{participant_id:02d}" for participant_id in range(1, 13)]
SCENES = [f"S{scene_id:02d}" for scene_id in range(1, 4)]
REPETITIONS = [1, 2]

QUANTITATIVE_MODALITIES = ["SpaceMouse", "Mouse2D", "Trackpad"]
QUALITATIVE_MODALITIES = ["SpaceMouse", "Mouse2D", "Trackpad", "HandGrab"]

MODALITY_PROFILES = {
    "SpaceMouse": {
        "translation_error_mean": 2.0,
        "translation_error_std": 0.6,
        "rotation_error_mean": 3.0,
        "rotation_error_std": 1.0,
        "completion_time_mean": 55.0,
        "completion_time_std": 8.0,
        "path_length_mean": 80.0,
        "path_length_std": 15.0,
        "nb_corrections_mean": 3.0,
        "success_probability": 0.98,
    },
    "Mouse2D": {
        "translation_error_mean": 5.0,
        "translation_error_std": 1.5,
        "rotation_error_mean": 8.0,
        "rotation_error_std": 2.5,
        "completion_time_mean": 90.0,
        "completion_time_std": 18.0,
        "path_length_mean": 150.0,
        "path_length_std": 40.0,
        "nb_corrections_mean": 7.0,
        "success_probability": 0.86,
    },
    "Trackpad": {
        "translation_error_mean": 4.0,
        "translation_error_std": 1.4,
        "rotation_error_mean": 6.5,
        "rotation_error_std": 2.2,
        "completion_time_mean": 78.0,
        "completion_time_std": 16.0,
        "path_length_mean": 130.0,
        "path_length_std": 35.0,
        "nb_corrections_mean": 6.0,
        "success_probability": 0.91,
    },
}


def ensure_output_directories() -> None:
    """Create local output directories when they do not exist yet."""
    RAW_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    QUALITATIVE_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)


def sample_positive_normal(
    rng: np.random.Generator,
    mean: float,
    std: float,
    minimum: float = 0.0,
) -> float:
    """Sample a normal value and clip it to a realistic positive range."""
    value = rng.normal(loc=mean, scale=std)
    return float(max(value, minimum))


def sample_vector_with_magnitude(
    rng: np.random.Generator,
    magnitude: float,
    dimensions: int = 3,
) -> np.ndarray:
    """Sample a random vector whose Euclidean norm equals the target magnitude."""
    direction = rng.normal(size=dimensions)
    direction_norm = np.linalg.norm(direction)

    if np.isclose(direction_norm, 0.0):
        direction = np.ones(dimensions)
        direction_norm = np.linalg.norm(direction)

    return direction / direction_norm * magnitude


def create_target_matrix(scene_id: str, rng: np.random.Generator) -> np.ndarray:
    """Create a scene-dependent target pose for the simulated 3D object."""
    scene_number = int(scene_id.replace("S", ""))
    base_translation = np.array([25.0 * scene_number, -12.0 * scene_number, 8.0])
    base_rotation = np.array([5.0 * scene_number, -3.0 * scene_number, 10.0])

    translation = base_translation + rng.normal(loc=0.0, scale=2.0, size=3)
    rotation = base_rotation + rng.normal(loc=0.0, scale=1.0, size=3)

    return create_transform_matrix(translation_mm=translation, rotation_deg=rotation)


def generate_quantitative_trials(rng: np.random.Generator) -> pd.DataFrame:
    """Generate one quantitative row per participant, scene, trial and modality."""
    rows: list[dict[str, object]] = []

    for participant_id in PARTICIPANTS:
        for scene_id in SCENES:
            for repetition in REPETITIONS:
                for modality in QUANTITATIVE_MODALITIES:
                    profile = MODALITY_PROFILES[modality]
                    target_matrix = create_target_matrix(scene_id, rng)

                    translation_error = sample_positive_normal(
                        rng,
                        profile["translation_error_mean"],
                        profile["translation_error_std"],
                        minimum=0.2,
                    )
                    rotation_error = sample_positive_normal(
                        rng,
                        profile["rotation_error_mean"],
                        profile["rotation_error_std"],
                        minimum=0.2,
                    )

                    translation_components = sample_vector_with_magnitude(
                        rng, translation_error
                    )
                    rotation_components = sample_vector_with_magnitude(rng, rotation_error)

                    error_matrix = create_transform_matrix(
                        translation_mm=translation_components,
                        rotation_deg=rotation_components,
                    )
                    final_matrix = target_matrix @ error_matrix

                    completion_time_s = sample_positive_normal(
                        rng,
                        profile["completion_time_mean"],
                        profile["completion_time_std"],
                        minimum=10.0,
                    )
                    path_length_mm = sample_positive_normal(
                        rng,
                        profile["path_length_mean"],
                        profile["path_length_std"],
                        minimum=20.0,
                    )
                    nb_corrections = int(
                        max(0, rng.poisson(lam=profile["nb_corrections_mean"]))
                    )
                    success = bool(rng.random() < profile["success_probability"])

                    rows.append(
                        {
                            "participant_id": participant_id,
                            "scene_id": scene_id,
                            "trial_id": repetition,
                            "modality": modality,
                            "target_matrix": matrix_to_json(target_matrix),
                            "final_matrix": matrix_to_json(final_matrix),
                            "tx_mm": round(float(translation_components[0]), 4),
                            "ty_mm": round(float(translation_components[1]), 4),
                            "tz_mm": round(float(translation_components[2]), 4),
                            "rx_deg": round(float(rotation_components[0]), 4),
                            "ry_deg": round(float(rotation_components[1]), 4),
                            "rz_deg": round(float(rotation_components[2]), 4),
                            "completion_time_s": round(completion_time_s, 3),
                            "path_length_mm": round(path_length_mm, 3),
                            "nb_corrections": nb_corrections,
                            "success": success,
                        }
                    )

    return pd.DataFrame(rows)


def weighted_choice(
    rng: np.random.Generator,
    values: list[int],
    probabilities: list[float],
) -> int:
    """Sample an integer score with explicit probabilities."""
    return int(rng.choice(values, p=probabilities))


def generate_preferred_modalities(rng: np.random.Generator) -> dict[str, str]:
    """Create participant-level preferences with SpaceMouse as the majority choice."""
    preferences = (
        ["SpaceMouse"] * 7
        + ["HandGrab"] * 3
        + ["Trackpad"]
        + ["Mouse2D"]
    )
    rng.shuffle(preferences)
    return dict(zip(PARTICIPANTS, preferences))


def generate_qualitative_scores(rng: np.random.Generator) -> pd.DataFrame:
    """Generate questionnaire-style scores for all qualitative modalities."""
    preferred_modalities = generate_preferred_modalities(rng)
    rows: list[dict[str, object]] = []

    for participant_id in PARTICIPANTS:
        for modality in QUALITATIVE_MODALITIES:
            if modality == "SpaceMouse":
                scores = {
                    "intuitiveness_score": weighted_choice(rng, [4, 5], [0.35, 0.65]),
                    "perceived_precision_score": weighted_choice(rng, [4, 5], [0.45, 0.55]),
                    "physical_discomfort_score": weighted_choice(rng, [1, 2], [0.7, 0.3]),
                    "surgical_relevance_score": weighted_choice(rng, [4, 5], [0.4, 0.6]),
                }
            elif modality == "Mouse2D":
                scores = {
                    "intuitiveness_score": weighted_choice(rng, [3, 4], [0.55, 0.45]),
                    "perceived_precision_score": weighted_choice(rng, [2, 3], [0.55, 0.45]),
                    "physical_discomfort_score": weighted_choice(rng, [1, 2], [0.75, 0.25]),
                    "surgical_relevance_score": weighted_choice(rng, [2, 3], [0.6, 0.4]),
                }
            elif modality == "Trackpad":
                scores = {
                    "intuitiveness_score": weighted_choice(rng, [3, 4], [0.6, 0.4]),
                    "perceived_precision_score": 3,
                    "physical_discomfort_score": weighted_choice(rng, [1, 2], [0.65, 0.35]),
                    "surgical_relevance_score": 3,
                }
            else:
                scores = {
                    "intuitiveness_score": weighted_choice(rng, [4, 5], [0.45, 0.55]),
                    "perceived_precision_score": weighted_choice(rng, [3, 4], [0.5, 0.5]),
                    "physical_discomfort_score": weighted_choice(rng, [1, 2], [0.6, 0.4]),
                    "surgical_relevance_score": 4,
                }

            rows.append(
                {
                    "participant_id": participant_id,
                    "modality": modality,
                    **scores,
                    "preferred_modality": preferred_modalities[participant_id],
                }
            )

    return pd.DataFrame(rows)


def main() -> None:
    """Generate and save the local demonstration datasets."""
    ensure_output_directories()
    rng = np.random.default_rng(RANDOM_SEED)

    quantitative_trials = generate_quantitative_trials(rng)
    qualitative_scores = generate_qualitative_scores(rng)

    quantitative_trials.to_csv(RAW_DATA_PATH, index=False)
    qualitative_scores.to_csv(QUALITATIVE_DATA_PATH, index=False)

    print(f"Generated quantitative logs: {RAW_DATA_PATH}")
    print(f"Generated qualitative scores: {QUALITATIVE_DATA_PATH}")
    print(f"Quantitative trials: {len(quantitative_trials)}")
    print(f"Qualitative rows: {len(qualitative_scores)}")


if __name__ == "__main__":
    main()
