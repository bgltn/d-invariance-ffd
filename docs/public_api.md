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
fracdiff_ffd(series, d, threshold, fill_method="ffill")
cat > docs/public_api.md <<'MD'
# Public API

This repository exposes public-safe methodology utilities for fixed-width fractional differencing and d-invariance testing.

The code exposes procedure, not empirical calibration.

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
