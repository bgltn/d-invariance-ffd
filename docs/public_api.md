# Public API

Public-safe methodology utilities for fixed-width fractional differencing (FFD) and d-invariance testing. The code exposes procedure, not empirical calibration.

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

### Fixed-width fractional differencing

- `get_ffd_weights(d, threshold)`
- `get_ffd_width(d, threshold)`
- `fracdiff_ffd(series, d, threshold, fill_method=None)`

Finite-window fractional differencing with weights truncated by a fixed threshold. Recursive coefficients are generated newest-to-oldest; the function returns the reversed (chronological) vector required by the rolling dot product, ordered from the oldest retained lag to the newest observation.

### Order selection

- `estimate_d(series, d_grid, threshold, alpha)`

Returns the smallest value `d` on the supplied grid for which the augmented Dickey–Fuller (ADF) test rejects the unit-root null at level `alpha` on the FFD-transformed series. The ADF rule follows López de Prado (2018, Chapter 5, snippet 5.4); full parameters are documented in `docs/methodology.md`.

Public defaults are illustrative. They are not the values used in the private research run.

### Invariance testing

- `compute_d_invariance_statistic(d_by_unit)`

Maximum pairwise absolute difference between selected orders across the units of an externally supplied admissible partition.

## Boundary contract

Segmentation boundaries are externally supplied. The package does not estimate regimes.

An admissible partition is either:

- a parent regime partition (regimes defined by structural breaks on VIX); or
- a child volatility-state partition refining one fixed regime (segments defined by NP-MOJO change points inside one regime).

Parent regimes must be ordered and non-overlapping. Child volatility states must lie inside one regime. A child boundary crossing a regime boundary is invalid.

FFD weights are not applied across boundaries. Validation and test observations do not enter order selection.

Different admissible partitions define different conditional tests.

## Missing-data contract

Default: `fill_method=None`. Missing observations remain in the input series; windows containing missing values are not transformed. The output index may be shorter than the input index. Downstream code must align by timestamp, not positional row number.

Forward fill (`fill_method="ffill"`) is available only as an explicit user choice and must be reported as a sensitivity specification.

The reported research audit returned: `STRICT PASS: FFD input series are complete. Forward fill was inactive.`

## Memory-preservation diagnostic

Pearson correlation between the original indexed series and the FFD-transformed series, following López de Prado (2018, Chapter 5, snippet 5.5). It characterises the operator and should be reported per regime or volatility state. The public repository does not report empirical values.

## Implementation note

The current implementation prioritises transparency over speed. A vectorised variant is planned.

## Disclosure boundary

Included: FFD utilities, order-selection logic, d-invariance statistic, boundary validation, leakage checks, synthetic examples, unit tests.

Excluded: private data, private feature names, raw file paths, forecasting logic, empirical calibration values, proprietary operator registries, private model-selection outputs.

## Synthetic example

`examples/synthetic_d_invariance.py` demonstrates segment construction, order selection, and the d-invariance statistic without private data.
