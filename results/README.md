# Frozen-operator registry

This directory holds the public frozen-operator registry, `frozen_operators.csv`. The registry documents selected operator outcomes from the d-invariance pipeline.

## Status

The file in this repository is a **schema placeholder**. It contains the column header in publication form but no data rows. The empirical content of the registry will be released alongside the manuscript via Zenodo. The split between GitHub (schema and method) and Zenodo (empirical content) is consistent with the project disclosure policy.

A researcher can:

- inspect the schema and field semantics in `docs/disclosure_policy.md`;
- inspect the validation logic in `src/audit/schema.py`;
- generate a schema-compliant example by running `examples/synthetic_d_invariance.py`.

## Schema

```text
feature_id, feature_class, scope, parent_regime_id, window_id, window_order,
d_star, adf_rejects, operator_status, bootstrap_p_value_bucket, n_obs_bin
```

Field semantics are documented in `docs/disclosure_policy.md`.

## Validation

Validate any registry file against the schema with:

```python
from audit.schema import read_and_validate_frozen_operator_registry

registry = read_and_validate_frozen_operator_registry("results/frozen_operators.csv")
```

The validator enforces required columns, allowed values, the parent-regime hierarchy, and operator-key uniqueness.

## Reproducibility

The Zenodo deposit will contain the populated `frozen_operators.csv` together with the manuscript and the methodology documents. The GitHub repository is the canonical source for the schema and the validation code. Any discrepancy between the two is resolved in favour of the GitHub schema definition.
