"""Utilities for creating and comparing 4x4 transformation matrices."""

from __future__ import annotations

import json
from typing import Iterable

import numpy as np


def rotation_matrix_from_euler_xyz(rotation_deg: Iterable[float]) -> np.ndarray:
    """Create a 3x3 rotation matrix from XYZ Euler angles in degrees."""
    rx_deg, ry_deg, rz_deg = rotation_deg
    rx, ry, rz = np.radians([rx_deg, ry_deg, rz_deg])

    cos_x, sin_x = np.cos(rx), np.sin(rx)
    cos_y, sin_y = np.cos(ry), np.sin(ry)
    cos_z, sin_z = np.cos(rz), np.sin(rz)

    rotation_x = np.array(
        [
            [1.0, 0.0, 0.0],
            [0.0, cos_x, -sin_x],
            [0.0, sin_x, cos_x],
        ]
    )
    rotation_y = np.array(
        [
            [cos_y, 0.0, sin_y],
            [0.0, 1.0, 0.0],
            [-sin_y, 0.0, cos_y],
        ]
    )
    rotation_z = np.array(
        [
            [cos_z, -sin_z, 0.0],
            [sin_z, cos_z, 0.0],
            [0.0, 0.0, 1.0],
        ]
    )

    # The convention is fixed in one place so generated and analyzed matrices match.
    return rotation_z @ rotation_y @ rotation_x


def create_transform_matrix(
    translation_mm: Iterable[float],
    rotation_deg: Iterable[float],
) -> np.ndarray:
    """Create a homogeneous 4x4 transform from translation and rotation."""
    matrix = np.eye(4)
    matrix[:3, :3] = rotation_matrix_from_euler_xyz(rotation_deg)
    matrix[:3, 3] = np.asarray(list(translation_mm), dtype=float)
    return matrix


def matrix_to_json(matrix: np.ndarray) -> str:
    """Serialize a 4x4 matrix as a compact JSON string for CSV storage."""
    return json.dumps(np.round(matrix.astype(float), 6).tolist())


def matrix_from_json(value: str) -> np.ndarray:
    """Deserialize a matrix stored as JSON text."""
    matrix = np.asarray(json.loads(value), dtype=float)
    if matrix.shape != (4, 4):
        raise ValueError(f"Expected a 4x4 matrix, got shape {matrix.shape}.")
    return matrix


def compute_relative_transform(target_matrix: np.ndarray, final_matrix: np.ndarray) -> np.ndarray:
    """Compute the relative transform T_error = inverse(T_target) @ T_final."""
    return np.linalg.inv(target_matrix) @ final_matrix


def compute_translation_error(transform_error: np.ndarray) -> float:
    """Compute Euclidean translation error in millimeters."""
    translation = transform_error[:3, 3]
    return float(np.linalg.norm(translation))


def compute_rotation_error(transform_error: np.ndarray) -> float:
    """Compute angular rotation error in degrees from a 3x3 rotation trace."""
    rotation = transform_error[:3, :3]
    trace_value = np.trace(rotation)

    # Numerical rounding can push the value slightly outside [-1, 1].
    cosine_angle = np.clip((trace_value - 1.0) / 2.0, -1.0, 1.0)
    angle_rad = np.arccos(cosine_angle)
    return float(np.degrees(angle_rad))

