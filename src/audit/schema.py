from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd


REQUIRED_FROZEN_OPERATOR_COLUMNS = (
    "feature_id",
    "feature_class",
    "scope",
    "window_id",
    "window_order",
    "d_star",
    "adf_rejects",
    "operator_status",
    "bootstrap_p_value_bucket",
    "used_for_operator_selection",
)


def validate_required_columns(
    data: pd.DataFrame,
    required_columns: Iterable[str],
) -> None:
    missing = set(required_columns).difference(data.columns)

    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")


def validate_no_nulls(
    data: pd.DataFrame,
    columns: Iterable[str],
) -> None:
    null_columns = [column for column in columns if data[column].isna().any()]

    if null_columns:
        raise ValueError(f"Columns contain null values: {null_columns}")


def validate_allowed_values(
    data: pd.DataFrame,
    column: str,
    allowed_values: Iterable[str],
) -> None:
    allowed = set(allowed_values)
    observed = set(data[column].dropna().astype(str))

    invalid = observed.difference(allowed)

    if invalid:
        raise ValueError(
            f"Column {column!r} contains invalid values: {sorted(invalid)}"
        )


def validate_unique_operator_keys(
    data: pd.DataFrame,
    key_columns: tuple[str, ...] = ("feature_id", "scope", "window_id"),
) -> None:
    duplicates = data.duplicated(list(key_columns))

    if duplicates.any():
        raise ValueError(
            f"Duplicate operator keys found for columns: {list(key_columns)}"
        )


def validate_frozen_operator_registry(
    registry: pd.DataFrame,
    *,
    allowed_scopes: tuple[str, ...] = ("REGIME", "SEGMENT"),
    allowed_operator_status: tuple[str, ...] = ("STATIONARY",),
) -> None:
    validate_required_columns(
        registry,
        REQUIRED_FROZEN_OPERATOR_COLUMNS,
    )

    validate_no_nulls(
        registry,
        (
            "feature_id",
            "feature_class",
            "scope",
            "window_id",
            "window_order",
            "d_star",
            "adf_rejects",
            "operator_status",
            "used_for_operator_selection",
        ),
    )

    validate_allowed_values(registry, "scope", allowed_scopes)
    validate_allowed_values(registry, "operator_status", allowed_operator_status)
    validate_unique_operator_keys(registry)

    if (registry["d_star"].astype(float) < 0).any():
        raise ValueError("d_star must be non-negative.")

    if (registry["window_order"].astype(int) < 1).any():
        raise ValueError("window_order must be positive.")


def read_and_validate_frozen_operator_registry(path: str | Path) -> pd.DataFrame:
    registry = pd.read_csv(path)
    validate_frozen_operator_registry(registry)
    return registry
