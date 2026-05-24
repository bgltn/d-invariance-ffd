import numpy as np
import pandas as pd
import pytest

from ffd.operator import (
    fracdiff_ffd,
    fracdiff_ffd_series,
    get_ffd_weights,
    get_ffd_width,
)


def test_weights_match_known_orders():
    assert np.allclose(
        get_ffd_weights(d=0.0, threshold=1e-12),
        np.array([1.0]),
    )

    assert np.allclose(
        get_ffd_weights(d=1.0, threshold=1e-12),
        np.array([-1.0, 1.0]),
    )

    w = get_ffd_weights(d=0.5, threshold=1e-12)

    # Weights are returned in chronological order:
    # [oldest lag, ..., newest observation].
    expected_chronological_tail = np.array([-0.0625, -0.125, -0.5, 1.0])

    assert np.allclose(w[-4:], expected_chronological_tail)


def test_width_expands_when_threshold_decreases():
    loose = get_ffd_width(d=0.5, threshold=1e-2)
    tight = get_ffd_width(d=0.5, threshold=1e-6)

    assert tight >= loose
    assert loose >= 1


def test_invalid_parameters_raise():
    with pytest.raises(ValueError):
        get_ffd_weights(d=-0.1, threshold=1e-5)

    with pytest.raises(ValueError):
        get_ffd_weights(d=1.1, threshold=1e-5)

    with pytest.raises(ValueError):
        get_ffd_weights(d=0.5, threshold=0.0)

    s = pd.Series([1.0, 2.0, 3.0])

    with pytest.raises(ValueError):
        fracdiff_ffd(s, d=0.5, threshold=1e-5, fill_method="bad")


def test_zero_order_returns_original_series():
    s = pd.Series(
        np.arange(1.0, 6.0),
        index=pd.date_range("2020-01-01", periods=5),
        name="x",
    )

    y = fracdiff_ffd(s, d=0.0, threshold=1e-12, fill_method=None)

    assert y.index.equals(s.index)
    assert np.allclose(y.to_numpy(), s.to_numpy())


def test_first_difference_of_constant_series_is_zero():
    s = pd.Series(
        np.ones(10),
        index=pd.date_range("2020-01-01", periods=10),
        name="x",
    )

    y = fracdiff_ffd(s, d=1.0, threshold=1e-12, fill_method=None)

    assert len(y) == 9
    assert np.allclose(y.to_numpy(), 0.0)


def test_transform_is_scale_equivariant():
    s = pd.Series(
        np.linspace(1.0, 20.0, 40),
        index=pd.date_range("2020-01-01", periods=40),
        name="x",
    )

    scale = 7.5

    y1 = fracdiff_ffd(s, d=0.5, threshold=1e-4, fill_method=None)
    y2 = fracdiff_ffd(scale * s, d=0.5, threshold=1e-4, fill_method=None)

    assert y1.index.equals(y2.index)
    assert np.allclose(y2.to_numpy(), scale * y1.to_numpy())


def test_does_not_forward_fill_by_default():
    s = pd.Series(
        [1.0, np.nan, 3.0, 4.0, 5.0],
        index=pd.date_range("2020-01-01", periods=5),
        name="x",
    )

    y = fracdiff_ffd(s, d=1.0, threshold=1e-12, fill_method=None)

    expected = pd.Series(
        [1.0, 1.0],
        index=s.index[-2:],
        name="x",
    )

    assert y.index.equals(expected.index)
    assert np.allclose(y.to_numpy(), expected.to_numpy())


def test_forward_fill_is_explicit():
    s = pd.Series(
        [1.0, np.nan, 3.0, 4.0, 5.0],
        index=pd.date_range("2020-01-01", periods=5),
        name="x",
    )

    y_none = fracdiff_ffd(s, d=1.0, threshold=1e-12, fill_method=None)
    y_ffill = fracdiff_ffd(s, d=1.0, threshold=1e-12, fill_method="ffill")

    assert len(y_ffill) > len(y_none)
    assert np.allclose(y_ffill.to_numpy(), np.array([0.0, 2.0, 1.0, 1.0]))


def test_notebook_wrapper_returns_series_and_width():
    s = pd.Series([1.0, 2.0, 3.0, 4.0])

    y, width = fracdiff_ffd_series(s, d=1.0, tau=1e-12, fill_method=None)

    assert isinstance(y, pd.Series)
    assert width == 2
    assert np.allclose(y.to_numpy(), np.array([1.0, 1.0, 1.0]))
