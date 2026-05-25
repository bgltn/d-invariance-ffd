# Research-to-Code Mapping

This document maps the public source modules to the research design described in `README.md` and `docs/methodology.md`. The repository exposes methodology utilities only. Empirical calibration, private feature names, raw data paths, forecasting target logic, and out-of-sample model code remain outside the public package.

## Research object

The study tests whether $`d^{\ast}`$, the minimum admissible fixed-width fractional differencing (FFD) order, is invariant across the segments of a fixed admissible partition: either the VIX-defined regime partition (parent), or an NP-MOJO volatility-state partition nested in one regime (child).

The object of inference is the preprocessing operator, not a downstream forecasting model. The hypothesis is stated at the level of the selected order $`d^{\ast}`$, not the operator parameter $`d`$.

## Module mapping

| Research component | Public module | Role |
|---|---|---|
| FFD operator | `ffd.operator` | Builds FFD weights with truncation threshold $`\tau`$ and applies the transform per segment. |
| Selection of $`d^{\ast}`$ | `ffd.estimator` | Selects the smallest $`d \in \mathcal{D}`$ satisfying the ADF rule. |
| d-invariance statistic | `ffd.invariance` | Computes $`\hat{T}_j = \max_{k \lt l}\ \bigl\|\hat{d}^{\ast}_{j,k} - \hat{d}^{\ast}_{j,l}\bigr\|`$ across the supplied partition. |
| Segment boundaries | `segmentation.boundaries` | Validates externally supplied non-overlapping windows under the boundary hierarchy. |
| Frozen-operator registry | `audit.schema` | Validates the anonymised publication artefact `results/frozen_operators.csv` against the public schema. |
| Public-safety check | `audit.leakage` | Validates that files do not contain caller-supplied forbidden strings before public release. |
| End-to-end demonstration | `examples/synthetic_d_invariance.py` | Constructs synthetic segments, selects $`d^{\ast}`$, and computes the d-invariance statistic without private data. |

## Boundary hierarchy

The pipeline uses a two-level boundary hierarchy, in line with the glossary in `README.md`.

1. **Parent regimes.** Regimes are defined by structural breaks on VIX, outside the FFD operator-selection step. They provide the parent estimation windows.
2. **Child volatility states.** NP-MOJO segmentation is applied inside each parent regime. Child volatility states cannot cross a regime boundary.
3. **Operator selection.** The selected order $`\hat{d}^{\ast}_{j,k}`$ is computed independently inside each admissible segment $`S_k`$. The FFD transform never crosses a regime or volatility-state boundary.

The d-invariance test is conditional on this hierarchy. A child boundary outside its parent regime is rejected by construction. Different admissible partitions define different conditional tests.

## Segmentation boundary convention

The public code does not implement NP-MOJO calibration. It accepts externally supplied boundary dates and converts them into non-overlapping windows.

A boundary date is interpreted as the first observation of the new segment. The full boundary contract is documented in `docs/public_api.md`.

## d-invariance statistic

For feature $`j`$ and a fixed admissible partition $`\mathcal{P} = \{S_1, \ldots, S_K\}`$:

```math
\hat{T}_j = \max_{1 \le k \lt l \le K} \bigl| \hat{d}^{\ast}_{j,k} - \hat{d}^{\ast}_{j,l} \bigr|.
```

The bootstrap calibration of $`\hat{T}_j`$ is described in `docs/methodology.md`.

## Disclosure boundary

The public modules expose procedure. They do not expose:

- raw licensed data;
- private feature names;
- raw paths;
- empirical calibration values;
- forecasting target logic;
- out-of-sample model code;
- proprietary operator registries.

The public artefact `results/frozen_operators.csv` is a publication registry, not the private operational registry.
