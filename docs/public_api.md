# Public API

This repository exposes public-safe methodology utilities for fixed-width fractional differencing and d-invariance testing.

The code does not include private data, private feature names, raw paths, forecasting logic, or empirical calibration values.

## Package layout

```text
src/
  ffd/
    operator.py
    estimator.py
    invariance.py

  segmentation/
    boundaries.py

  audit/
    schema.py
    leakage.py
get_ffd_weights(d, threshold)
get_ffd_width(d, threshold)
fracdiff_ffd(series, d, threshold, fill_method=None)
cat > docs/public_api.md <<'MD'

# Public API

This repository exposes public-safe methodology utilities for fixed-width fractional differencing and d-invariance testing.

The code exposes procedure, not empirical calibration.

### Boundary contract

The public API treats segmentation boundaries as externally supplied inputs. The package does not estimate volatility regimes. It validates whether supplied boundaries are ordered, non-overlapping, and admissible.

The expected contract is:

- parent regimes must be non-overlapping;
- child segments must lie inside one parent regime;
- FFD weights must not be applied across a boundary;
- validation and test observations must not enter the estimation of \(d^*\).

This design separates boundary construction from operator-stability testing.

## Package layout

```text
src/
  ffd/
    operator.py
    estimator.py
    invariance.py

  segmentation/
    boundaries.py

  audit/
    schema.py
    leakage.py

