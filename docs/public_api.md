# Public API

This repository exposes public-safe methodology utilities for Fixed-width Fractional Differencing and d-invariance testing.

The code exposes procedure, not empirical calibration. It does not include private data, private feature names, raw paths, forecasting logic, or empirical calibration values.

## Package layout

- `src/ffd/operator.py`
- `src/ffd/estimator.py`
- `src/ffd/invariance.py`
- `src/segmentation/boundaries.py`
- `src/audit/schema.py`
- `src/audit/leakage.py`
- `tests/test_ffd_operator.py`
- `tests/test_invariance.py`
- `tests/test_boundaries.py`
- `tests/test_schema.py`
- `tests/test_leakage.py`
- `examples/synthetic_d_invariance.py`

## Core functions

### Fixed-width Fractional Differencing

- `get_ffd_weights(d, threshold)`
- `get_ffd_width(d, threshold)`
- `fracdiff_ffd(series, d, threshold, fill_method=None)`

The operator applies finite-window fractional differencing with weights truncated by a fixed threshold. The returned weights are ordered chronologically, from the oldest retained lag to the newest observation, so they can be applied directly to a chronological rolling window.

The recursive fractional-differencing coefficients are generated in newest-to-oldest order. The public function returns the reversed chronological vector required by the rolling dot product.

### Order selection

- `estimate_d(series, d_grid, threshold, alpha)`

The selected order `d*` is the smallest admissible value on the supplied grid that satisfies the stationarity rule implemented in `src/ffd/estimator.py`.

The public repository exposes the selection rule and callable interface. Public defaults are illustrative and are not the empirical calibration values used in the private research run.

### Invariance testing

- `compute_d_invariance_statistic(d_by_unit)`

The d-invariance statistic compares selected orders across admissible operator units. The public implementation treats each regime or segment as an externally supplied unit.

## Boundary contract

The public API treats segmentation boundaries as externally supplied inputs. The package does not estimate volatility regimes.

An admissible partition may be either:

- a parent volatility-regime partition; or
- a child segmentation that refines one fixed parent partition.

The hierarchy is strict. Parent regimes must be ordered and non-overlapping. Child segments must lie inside one parent regime. A child boundary that crosses a parent-regime boundary is invalid.

Different admissible parent partitions define different conditional d-invariance tests. Different admissible child refinements of the same parent partition define different within-regime conditional tests.

Fixed-width Fractional Differencing weights must not be applied across a parent or child boundary. Validation and test observations must not enter the estimation of `d*`.

This design separates boundary construction from operator-stability testing.

## Missing-data contract

Forward fill is not the default missing-data policy.

The default behaviour is `fill_method=None`.

Under this setting, missing observations remain in the input series. Windows containing missing values are not transformed. The returned transformed series contains only timestamps for which the retained FFD window is finite.

This means the output index may be shorter than the input index. Downstream code must align transformed series by timestamp, not by positional row number.

Forward fill is available only as an explicit user choice: `fill_method="ffill"`.

When forward fill is used, the transformed series, the selected order `d*`, and the memory-preservation diagnostic are conditional on that imputation rule. Users should report this as a sensitivity specification.

The reported research audit returned: `STRICT PASS: FFD input series are complete. Forward fill was inactive.`

This statement discloses no feature names, dates, values, calibration constants, or empirical results. It only states that carry-forward imputation did not affect the reported operator-selection run.

## Memory-preservation diagnostic

The memory-preservation diagnostic is the Pearson correlation between the original indexed series and the Fixed-width Fractional Differencing transformed series, following López de Prado's convention for assessing memory preservation after fractional differencing.

This diagnostic characterises the operator. It should be reported per regime or segment in the publication. The public repository does not report empirical values.

## Implementation note

The current finite impulse response implementation prioritises transparency over speed. It uses an explicit loop over retained windows and `numpy.dot`.

This is acceptable for the synthetic example and for auditability. For long series with small `d`, the retained width can become large. A vectorised implementation using `numpy.convolve` or `scipy.signal.lfilter` is a planned optimisation.

## Disclosure boundary

The repository releases methodology, not signal construction.

It includes:

- Fixed-width Fractional Differencing utilities;
- d-order selection logic;
- d-invariance statistic utilities;
- boundary validation;
- leakage checks;
- synthetic examples;
- unit tests.

It excludes:

- private data;
- private feature names;
- raw file paths;
- forecasting logic;
- empirical calibration values;
- proprietary operator registries;
- private model-selection outputs.

## Synthetic example

A public-safe synthetic example is available at `examples/synthetic_d_invariance.py`.

The example demonstrates segment construction, `d*` estimation, and the d-invariance statistic without private data or empirical calibration.
