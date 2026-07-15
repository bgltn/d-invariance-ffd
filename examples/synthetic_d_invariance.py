"""Synthetic end-to-end example of the d-invariance pipeline.

Generates a synthetic feature, segments it under a two-level boundary
hierarchy (parent regimes; child segments), selects d* per segment,
computes the d-invariance statistic, and writes a schema-compliant
frozen-operator registry to disk.

The example uses no private data and no empirical calibration. It demonstrates
the public interface and the publication schema. Run from the repository root:

    PYTHONPATH=src python examples/synthetic_d_invariance.py
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from audit.schema import (
    ALLOWED_BOOTSTRAP_P_VALUE_BUCKETS,
    ALLOWED_N_OBS_BINS,
    validate_frozen_operator_registry,
)
from ffd import compute_d_invariance_statistic, estimate_d_star
from segmentation import build_segments_from_boundaries


OUTPUT_PATH = Path("results") / "synthetic_frozen_operators.csv"


def make_synthetic_series(n: int = 600, seed: int = 7) -> pd.Series:
    """Random walk with mild structural breaks in drift."""
    rng = np.random.default_rng(seed)
    innovations = rng.standard_normal(n)
    drift = np.concatenate(
        [
            np.zeros(n // 3),
            0.05 * np.ones(n // 3),
            -0.03 * np.ones(n - 2 * (n // 3)),
        ]
    )
    values = np.cumsum(innovations + drift)

    index = pd.date_range("2020-01-01", periods=n, freq="B")
    return pd.Series(values, index=index, name="synthetic_feature")


def bucket_n_obs(n: int) -> str:
    if n < 200:
        return "<200"
    if n < 500:
        return "200-500"
    if n < 1000:
        return "500-1000"
    if n < 2000:
        return "1000-2000"
    return ">2000"


def bucket_p_value(p_value: float) -> str:
    if p_value < 0.01:
        return "p<0.01"
    if p_value < 0.10:
        return "0.01<=p<0.10"
    return "p>=0.10"


def synthesise_regime_partition(series: pd.Series) -> pd.DataFrame:
    """Two parent regimes split at the mid-point of the series."""
    midpoint = series.index[len(series) // 2]
    regimes = build_segments_from_boundaries(
        series.index,
        boundaries=[midpoint.strftime("%Y-%m-%d")],
        min_obs=50,
    )
    regimes["regime_id"] = [f"regime_{i + 1}" for i in range(len(regimes))]
    return regimes


def synthesise_segments(series: pd.Series, regime: pd.Series) -> pd.DataFrame:
    """Two child segments inside the supplied regime."""
    window = series.loc[regime["start"] : regime["end"]]
    if len(window) < 100:
        return pd.DataFrame()

    midpoint = window.index[len(window) // 2]
    states = build_segments_from_boundaries(
        window.index,
        boundaries=[midpoint.strftime("%Y-%m-%d")],
        min_obs=50,
    )
    states["parent_regime_id"] = regime["regime_id"]
    states["segment_id"] = [
        f"{regime['regime_id']}_segment_{i + 1}" for i in range(len(states))
    ]
    return states


def estimate_on_window(
    series: pd.Series,
    window_start,
    window_end,
    feature_id: str,
) -> dict:
    window = series.loc[window_start:window_end]

    result = estimate_d_star(
        series=window,
        d_grid=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
        threshold=1e-3,
        adf_alpha=0.05,
        min_obs=30,
        feature=feature_id,
    )

    return {
        "d_star": result.d_star,
        "adf_rejects": bool(result.adf_rejects),
        "n_obs": int(len(window.dropna())),
    }


def build_registry(series: pd.Series, feature_id: str) -> pd.DataFrame:
    regimes = synthesise_regime_partition(series)

    records = []

    # Parent regimes
    for order, regime in enumerate(regimes.itertuples(), start=1):
        estimate = estimate_on_window(
            series, regime.start, regime.end, feature_id
        )
        records.append(
            {
                "feature_id": feature_id,
                "feature_class": "LEVEL",
                "scope": "REGIME",
                "parent_regime_id": pd.NA,
                "window_id": regime.regime_id,
                "window_order": order,
                "d_star": estimate["d_star"],
                "adf_rejects": estimate["adf_rejects"],
                "operator_status": "STATIONARY"
                if estimate["adf_rejects"]
                else "NON_STATIONARY",
                "bootstrap_p_value_bucket": bucket_p_value(0.5),
                "n_obs_bin": bucket_n_obs(estimate["n_obs"]),
            }
        )

    # Child 
    for _, regime in regimes.iterrows():
        states = synthesise_segments(series, regime)
        for order, state in enumerate(states.itertuples(), start=1):
            estimate = estimate_on_window(
                series, state.start, state.end, feature_id
            )
            records.append(
                {
                    "feature_id": feature_id,
                    "feature_class": "LEVEL",
                    "scope": "SEGMENT",
                    "parent_regime_id": state.parent_regime_id,
                    "window_id": state.segment_id,
                    "window_order": order,
                    "d_star": estimate["d_star"],
                    "adf_rejects": estimate["adf_rejects"],
                    "operator_status": "STATIONARY"
                    if estimate["adf_rejects"]
                    else "NON_STATIONARY",
                    "bootstrap_p_value_bucket": bucket_p_value(0.5),
                    "n_obs_bin": bucket_n_obs(estimate["n_obs"]),
                }
            )

    registry = pd.DataFrame.from_records(records)
    registry = registry.dropna(subset=["d_star"]).reset_index(drop=True)
    return registry


def main() -> None:
    series = make_synthetic_series()
    registry = build_registry(series, feature_id="synthetic_feature_001")

    # Keep only rows where the operator status is in the allowed set used by
    # the public validator. The synthetic example may produce NON_STATIONARY
    # rows; those would fail validation under the default allowed_operator_status.
    registry = registry.loc[registry["operator_status"] == "STATIONARY"].reset_index(
        drop=True
    )

    validate_frozen_operator_registry(registry)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    registry.to_csv(OUTPUT_PATH, index=False)

    statistic = compute_d_invariance_statistic(
        registry.rename(columns={"d_star": "d_star"})
    )

    print(f"Wrote schema-compliant registry to {OUTPUT_PATH}")
    print(f"Allowed bootstrap_p_value buckets: {ALLOWED_BOOTSTRAP_P_VALUE_BUCKETS}")
    print(f"Allowed n_obs bins: {ALLOWED_N_OBS_BINS}")
    print()
    print("Registry preview:")
    print(registry.to_string(index=False))
    print()
    print("d-invariance statistic:")
    print(statistic.to_string(index=False))


if __name__ == "__main__":
    main()
