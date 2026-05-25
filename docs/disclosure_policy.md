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

A public-safe frozen-operator registry may be released when it is anonymised and publication-ready. It may contain the following fields:

```text
feature_id
feature_class
scope
window_id
window_order
d_star
adf_rejects
operator_status
bootstrap_p_value_bucket
used_for_operator_selection
n_obs_bin
```

`feature_class` reports the transformation class (for example, `LOG_LEVEL` or `LEVEL`). It does not report the economic asset class, country, ticker, maturity, vendor identifier, or signal role.

The registry is a publication artefact, not the private operational registry.
