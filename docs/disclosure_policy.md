# Disclosure Policy

## Principle

This repository follows one disclosure rule:

> Release the methodology; protect the signal.

The public repository is designed to support methodological review, not trading replication.

## Public Material

The following material may be included in the repository:

- methodological documentation;
- fixed-width fractional differencing logic;
- d-invariance hypothesis definition;
- stationary-bootstrap test design;
- public-safe configuration templates;
- anonymised frozen-operator registry;
- reproducibility and leakage-control notes.

## Excluded Material

The following material must not be committed:

- raw licensed data;
- raw vendor files;
- feature names;
- feature-name decoders;
- private `FEATURE_CLASS_MAP` objects;
- Bloomberg or vendor identifiers;
- exact private calibration schedules;
- raw bootstrap p-values;
- exact bootstrap seeds;
- operational model-selection grids;
- private notebooks with outputs;
- trading rules;
- portfolio-construction logic;
- confidential manuscript drafts.

## Public Registry

The file `results/frozen_operators.csv` is a public-safe publication registry.

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
```

It must not contain:

```text
feature
ticker
target
vendor
asset
source_start_date
source_end_date
application_start_date
application_end_date
parent_regime_id
segment_id
raw p_value
bootstrap seed
bootstrap repetitions
tau
D-grid
raw data
transformed feature values
```

## Feature-Class Rule

`feature_class` reports only the transformation class.

Allowed examples:

```text
LOG_LEVEL
LEVEL
```

It must not report economic identity, country, currency, maturity, vendor ticker, signal role, or asset-specific interpretation.

## Confidentiality Boundary

The private research pipeline, full empirical notebook, raw data, feature map, calibration files, and manuscript drafts remain confidential. A private GitHub repository is a staging area, not a disclosure boundary.

## Pre-Commit Check

Before every commit, run a local leakage scan against private project terms, raw-data filenames, vendor identifiers, feature decoders, and confidential manuscript names.

The exact scan pattern is private and must not be committed.

Expected result: no private identifiers, raw-data references, private calibration objects, or confidential manuscript references should appear in public files.

If the scan returns any file path, inspect and remove the leak before committing.
