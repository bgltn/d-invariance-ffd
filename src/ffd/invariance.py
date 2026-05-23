from __future__ import annotations

from dataclasses import asdict, dataclass
from itertools import combinations

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class DInvarianceResult:
    feature: str
    n_windows: int
    t_stat: float | None
    d_min: float | None
    d_max: float | None
    status: str

    def to_dict(self) -> dict:
        return asdict(self)


def compute_pairwise_deltas(
    registry: pd.DataFrame,
    *,
    feature_col: str = "feature_id",
    window_col: str = "window_id",
    d_col: str = "d_star",
    window_order_col: str | None = "window_order",
) -> pd.DataFrame:
    required = {feature_col, window_col, d_col}
    missing = required.difference(registry.columns)

    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    records = []

    for feature, group in registry.dropna(subset=[d_col]).groupby(feature_col):
        if window_order_col is not None and window_order_col in group.columns:
            group = group.sort_values(window_order_col)
        else:
            group = group.sort_values(window_col)

        rows = group[[window_col, d_col]].drop_duplicates().to_dict("records")

        for left, right in combinations(rows, 2):
            delta = float(left[d_col]) - float(right[d_col])

            records.append(
                {
                    "feature": str(feature),
                    "left_window": left[window_col],
                    "right_window": right[window_col],
                    "left_d_star": float(left[d_col]),
                    "right_d_star": float(right[d_col]),
                    "delta": delta,
                    "abs_delta": abs(delta),
                }
            )

    return pd.DataFrame.from_records(records)


def compute_d_invariance_statistic(
    registry: pd.DataFrame,
    *,
    feature_col: str = "feature_id",
    window_col: str = "window_id",
    d_col: str = "d_star",
    window_order_col: str | None = "window_order",
) -> pd.DataFrame:
    required = {feature_col, window_col, d_col}
    missing = required.difference(registry.columns)

    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    deltas = compute_pairwise_deltas(
        registry,
        feature_col=feature_col,
        window_col=window_col,
        d_col=d_col,
        window_order_col=window_order_col,
    )

    records = []

    for feature, group in registry.dropna(subset=[d_col]).groupby(feature_col):
        d_values = group[d_col].astype(float).to_numpy()
        n_windows = int(group[window_col].nunique())

        if n_windows < 2:
            result = DInvarianceResult(
                feature=str(feature),
                n_windows=n_windows,
                t_stat=None,
                d_min=float(np.min(d_values)) if len(d_values) else None,
                d_max=float(np.max(d_values)) if len(d_values) else None,
                status="INSUFFICIENT_WINDOWS",
            )
        else:
            feature_deltas = deltas.loc[deltas["feature"] == str(feature), "abs_delta"]

            result = DInvarianceResult(
                feature=str(feature),
                n_windows=n_windows,
                t_stat=float(feature_deltas.max()),
                d_min=float(np.min(d_values)),
                d_max=float(np.max(d_values)),
                status="OK",
            )

        records.append(result.to_dict())

    return pd.DataFrame.from_records(records)


def bootstrap_p_value(
    observed_statistic: float,
    bootstrap_statistics: np.ndarray | list[float],
) -> float:
    observed = float(observed_statistic)
    boot = np.asarray(bootstrap_statistics, dtype=float)
    boot = boot[np.isfinite(boot)]

    if boot.size == 0:
        raise ValueError("bootstrap_statistics contains no finite values.")

    exceedances = int(np.sum(boot >= observed))

    return float((exceedances + 1) / (boot.size + 1))


def attach_bootstrap_p_values(
    statistic_table: pd.DataFrame,
    bootstrap_table: pd.DataFrame,
    *,
    feature_col: str = "feature",
    statistic_col: str = "t_stat",
    bootstrap_stat_col: str = "bootstrap_t_stat",
) -> pd.DataFrame:
    required_stats = {feature_col, statistic_col}
    required_boot = {feature_col, bootstrap_stat_col}

    missing_stats = required_stats.difference(statistic_table.columns)
    missing_boot = required_boot.difference(bootstrap_table.columns)

    if missing_stats:
        raise ValueError(f"Missing statistic table columns: {sorted(missing_stats)}")
    if missing_boot:
        raise ValueError(f"Missing bootstrap table columns: {sorted(missing_boot)}")

    output = statistic_table.copy()
    p_values = []

    for _, row in output.iterrows():
        feature = row[feature_col]
        observed = row[statistic_col]

        boot = bootstrap_table.loc[
            bootstrap_table[feature_col] == feature,
            bootstrap_stat_col,
        ]

        if pd.isna(observed) or boot.empty:
            p_values.append(np.nan)
        else:
            p_values.append(bootstrap_p_value(observed, boot.to_numpy()))

    output["bootstrap_p_value"] = p_values

    return output
