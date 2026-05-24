# Disclosure Policy

## Principle

The public repository supports methodological review. It is not designed to reproduce private trading signals, private empirical calibration, or proprietary data construction.

## Public Material

The following material may be included in the repository:

- methodological documentation;
- Fixed-width Fractional Differencing utilities;
- d-invariance hypothesis definition;
- stationary-bootstrap test design;
- public-safe configuration templates;
- anonymised publication registries;
- reproducibility notes;
- leakage-control notes;
- synthetic examples;
- unit tests.

## Excluded Material

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

## Public Registry

A public-safe frozen-operator registry may be released when it is anonymised and publication-ready.

It may contain:

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
