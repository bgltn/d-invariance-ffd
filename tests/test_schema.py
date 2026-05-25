import pandas as pd
import pytest

from audit.schema import validate_frozen_operator_registry


def make_valid_registry():
    return pd.DataFrame(
        {
            "feature_id": ["feature_001", "feature_001"],
            "feature_class": ["LEVEL", "LEVEL"],
            "scope": ["REGIME", "SEGMENT"],
            "parent_regime_id": [None, "regime_1"],
            "window_id": ["regime_1", "segment_1"],
            "window_order": [1, 1],
            "d_star": [0.10, 0.20],
            "adf_rejects": [True, True],
            "operator_status": ["STATIONARY", "STATIONARY"],
            "bootstrap_p_value_bucket": ["p<0.01", "p>=0.10"],
            "n_obs_bin": ["500-1000", "200-500"],
        }
    )


def test_valid_frozen_operator_registry_passes():
    registry = make_valid_registry()

    validate_frozen_operator_registry(registry)


def test_missing_required_column_fails():
    registry = make_valid_registry().drop(columns=["d_star"])

    with pytest.raises(ValueError, match="Missing required columns"):
        validate_frozen_operator_registry(registry)


def test_missing_parent_regime_id_column_fails():
    registry = make_valid_registry().drop(columns=["parent_regime_id"])

    with pytest.raises(ValueError, match="Missing required columns"):
        validate_frozen_operator_registry(registry)


def test_missing_n_obs_bin_column_fails():
    registry = make_valid_registry().drop(columns=["n_obs_bin"])

    with pytest.raises(ValueError, match="Missing required columns"):
        validate_frozen_operator_registry(registry)


def test_invalid_scope_fails():
    registry = make_valid_registry()
    registry.loc[0, "scope"] = "PRIVATE_SCOPE"

    with pytest.raises(ValueError, match="invalid values"):
        validate_frozen_operator_registry(registry)


def test_invalid_bootstrap_p_value_bucket_fails():
    registry = make_valid_registry()
    registry.loc[0, "bootstrap_p_value_bucket"] = "low"

    with pytest.raises(ValueError, match="invalid values"):
        validate_frozen_operator_registry(registry)


def test_invalid_n_obs_bin_fails():
    registry = make_valid_registry()
    registry.loc[0, "n_obs_bin"] = "tiny"

    with pytest.raises(ValueError, match="invalid values"):
        validate_frozen_operator_registry(registry)


def test_negative_d_star_fails():
    registry = make_valid_registry()
    registry.loc[0, "d_star"] = -0.10

    with pytest.raises(ValueError, match="d_star must be non-negative"):
        validate_frozen_operator_registry(registry)


def test_duplicate_operator_keys_fail():
    registry = make_valid_registry()
    registry.loc[1, "scope"] = "REGIME"
    registry.loc[1, "window_id"] = "regime_1"
    registry.loc[1, "parent_regime_id"] = None

    with pytest.raises(ValueError, match="Duplicate operator keys"):
        validate_frozen_operator_registry(registry)


def test_parent_regime_id_required_for_segment_rows():
    registry = make_valid_registry()
    registry.loc[1, "parent_regime_id"] = None

    with pytest.raises(
        ValueError,
        match="parent_regime_id must be populated for all SEGMENT rows",
    ):
        validate_frozen_operator_registry(registry)


def test_parent_regime_id_must_be_null_for_regime_rows():
    registry = make_valid_registry()
    registry.loc[0, "parent_regime_id"] = "regime_1"

    with pytest.raises(
        ValueError,
        match="parent_regime_id must be null for REGIME rows",
    ):
        validate_frozen_operator_registry(registry)
