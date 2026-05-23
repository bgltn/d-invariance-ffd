import pandas as pd
import pytest

from audit.schema import validate_frozen_operator_registry


def make_valid_registry():
    return pd.DataFrame(
        {
            "feature_id": ["feature_001", "feature_001"],
            "feature_class": ["LEVEL", "LEVEL"],
            "scope": ["REGIME", "SEGMENT"],
            "window_id": ["regime_1", "segment_1"],
            "window_order": [1, 1],
            "d_star": [0.10, 0.20],
            "adf_rejects": [True, True],
            "operator_status": ["STATIONARY", "STATIONARY"],
            "bootstrap_p_value_bucket": ["low", "high"],
            "used_for_operator_selection": [False, False],
        }
    )


def test_valid_frozen_operator_registry_passes():
    registry = make_valid_registry()

    validate_frozen_operator_registry(registry)


def test_missing_required_column_fails():
    registry = make_valid_registry().drop(columns=["d_star"])

    with pytest.raises(ValueError, match="Missing required columns"):
        validate_frozen_operator_registry(registry)


def test_invalid_scope_fails():
    registry = make_valid_registry()
    registry.loc[0, "scope"] = "PRIVATE_SCOPE"

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

    with pytest.raises(ValueError, match="Duplicate operator keys"):
        validate_frozen_operator_registry(registry)
