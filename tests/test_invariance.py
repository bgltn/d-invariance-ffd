import numpy as np
import pandas as pd

from ffd.invariance import (
    attach_bootstrap_p_values,
    bootstrap_p_value,
    compute_d_invariance_statistic,
    compute_pairwise_deltas,
)


def test_constant_segment_orders_return_zero_statistic():
    registry = pd.DataFrame(
        {
            "feature_id": ["feature_a", "feature_a", "feature_a"],
            "window_id": ["w1", "w2", "w3"],
            "window_order": [1, 2, 3],
            "d_star": [0.25, 0.25, 0.25],
        }
    )

    result = compute_d_invariance_statistic(registry)

    assert result.loc[0, "feature"] == "feature_a"
    assert result.loc[0, "n_windows"] == 3
    assert result.loc[0, "t_stat"] == 0.0
    assert result.loc[0, "status"] == "OK"


def test_pairwise_deltas_return_maximum_absolute_difference():
    registry = pd.DataFrame(
        {
            "feature_id": ["feature_a", "feature_a", "feature_a"],
            "window_id": ["w1", "w2", "w3"],
            "window_order": [1, 2, 3],
            "d_star": [0.10, 0.30, 0.20],
        }
    )

    deltas = compute_pairwise_deltas(registry)
    result = compute_d_invariance_statistic(registry)

    assert len(deltas) == 3
    assert np.isclose(result.loc[0, "t_stat"], 0.20)


def test_bootstrap_p_value_uses_plus_one_correction():
    p_value = bootstrap_p_value(
        observed_statistic=0.5,
        bootstrap_statistics=np.array([0.1, 0.2, 0.6]),
    )

    assert p_value == 0.5


def test_attach_bootstrap_p_values():
    statistic_table = pd.DataFrame(
        {
            "feature": ["feature_a"],
            "t_stat": [0.5],
        }
    )

    bootstrap_table = pd.DataFrame(
        {
            "feature": ["feature_a", "feature_a", "feature_a"],
            "bootstrap_t_stat": [0.1, 0.2, 0.6],
        }
    )

    result = attach_bootstrap_p_values(statistic_table, bootstrap_table)

    assert result.loc[0, "bootstrap_p_value"] == 0.5
