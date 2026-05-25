# Disclosure policy

## Principle

The public repository supports methodological review. It is not designed to reproduce private trading signals, private empirical calibration, or proprietary data construction.

## Public material

The following material may be included in the repository:

- methodological documentation;
- fixed-width fractional differencing (FFD) utilities;
- d-invariance hypothesis definition;
- stationary-bootstrap test design;
- public-safe configuration templates;
- anonymised publication registries;
- reproducibility notes;
- leakage-control notes;
- synthetic examples;
- unit tests.

## Excluded material

The following material must not be committed:

- raw licensed data;
- raw vendor files;
- private feature names;
- feature-name decoders;
- private feature-mapping objects;
- licensed market-data provider identifiers;
- exact private calibration schedules;
- raw bootstrap p-values;
- exact bootstrap seeds;
- operational model-selection grids;
- private notebooks with outputs;
- trading rules;
- portfolio-construction logic;
- confidential manuscript drafts.

Bootstrap seeds are excluded because, combined with the public registry schema, they could enable partial reverse-engineering of private feature identifiers. Reproducibility is supported at the methodological level (procedure, statistic, test design), not at the bit-exact level.

## Public registry

The frozen-operator registry is a publication artefact, not the private operational registry. It will be released alongside the manuscript via Zenodo. The public GitHub repository contains the schema definition and validation logic, not the empirical content.

### Schema

The registry contains the following fields:

```text
feature_id
feature_class
scope
parent_regime_id
window_id
window_order
d_star
adf_rejects
operator_status
bootstrap_p_value_bucket
n_obs_bin
```

### Field semantics

- `feature_id`: anonymised identifier. Does not reveal asset class, country, ticker, maturity, vendor, or signal role.
- `feature_class`: transformation class (for example, `LOG_LEVEL` or `LEVEL`). Does not reveal the economic interpretation of the feature.
- `scope`: one of `REGIME` (parent partition) or `SEGMENT` (child volatility state).
- `parent_regime_id`: identifier of the parent regime. Required for `SEGMENT` rows. Null for `REGIME` rows.
- `window_id`: anonymised identifier of the regime or volatility state.
- `window_order`: positive integer indicating the temporal order of the window within its scope.
- `d_star`: selected fractional differencing order. Non-negative real number on the candidate grid.
- `adf_rejects`: boolean indicating whether the ADF test rejects the unit-root null at the configured level.
- `operator_status`: classification of the selected operator. Currently restricted to `STATIONARY`.
- `bootstrap_p_value_bucket`: one of `p<0.01`, `0.01<=p<0.10`, `p>=0.10`. Raw p-values are not disclosed.
- `n_obs_bin`: one of `<200`, `200-500`, `500-1000`, `1000-2000`, `>2000`. Bucketed to preserve anonymity.
