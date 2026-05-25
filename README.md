# Testing the d-Invariance Hypothesis for the Fixed-Width Fractional Differencing Operator Across Volatility States Using VIX
[![DOI](https://zenodo.org/badge/1247172897.svg)](https://doi.org/10.5281/zenodo.20384552)

**Author:** T. Niero
**Project page:** https://bgltn.github.io/d-invariance-ffd/

## Overview

This repository is a research compendium for testing whether the fixed-width fractional differencing (FFD) operator is stable across volatility states defined inside VIX-based regimes. The object of inference is operator stability, not the estimation of a latent long-memory parameter.

The workflow conditions on VIX-defined regimes and tests the stability of $d^{*}$ across NP-MOJO volatility states. Inference is conducted by stationary bootstrap. Predictive evaluation is supporting material only, under a train-only frozen-operator protocol and a sealed out-of-sample design.

## Terminology

| Term | Definition |
|---|---|
| $d$ | Fractional differencing order; a parameter of the FFD operator on grid $\mathcal{D}$. |
| $d^{*}$ | Minimum $d \in \mathcal{D}$ for which the augmented Dickey–Fuller (ADF) test rejects the unit-root null at level $\alpha$. |
| **Regime** | Time interval delimited by structural breaks on VIX. Parent partition, exogenous to the feature. |
| **Volatility state** (segment) | Time interval inside one regime, delimited by NP-MOJO change points. Child partition. |
| Admissible partition | The regime partition, or the volatility-state partition inside a fixed regime. |

The hypothesis is stated at the level of the selected order $d^{*}$, not the operator parameter $d$.

## Research question

Does $d^{*}$ remain invariant across the volatility states inside each VIX-defined regime when the FFD operator specification is held fixed?

"Fixed operator specification" denotes that the FFD implementation, truncation threshold $\tau$, candidate grid $\mathcal{D}$, and ADF-based stationarity-selection rule are held constant across segments; only the data subset changes. The question concerns the stability of the selected order $d^{*}$, not time variation in a long-memory parameter.

## Formal hypothesis

For a fixed admissible partition $`\mathcal{P} = \{S_1, \ldots, S_K\}`$ and feature $`j`$, let $`\hat{d}^{\ast}_{j,k}`$ denote the selected order on segment $`S_k`$. The null hypothesis is that the selected order is constant across the partition:

```math
H_{0,j}: \quad d^{\ast}_{j,1} = \cdots = d^{\ast}_{j,K}.
```

The test statistic is the maximum pairwise absolute difference between segment-specific selected orders:

```math
\hat{T}_j = \max_{1 \le k \lt l \le K} \bigl| \hat{d}^{\ast}_{j,k} - \hat{d}^{\ast}_{j,l} \bigr|.
```

Inference is conducted by stationary bootstrap (Politis and Romano, 1994), drawn independently within each fixed segment, with the bootstrap statistic recentred around $`\hat{d}^{\ast}_{j,k}`$. The full statement, including bootstrap parameters and decision rule, is provided in `docs/methodology.md`.

The public repository reports anonymised registry outputs and bucketed bootstrap evidence. Raw p-values and private calibration are excluded.


## Pipeline

1. Structural-break detection on VIX defines the parent regimes.
2. NP-MOJO segmentation within each regime defines the child volatility states.
3. The FFD operator is applied with fixed specification.
4. The minimum admissible order $d^{*}$ is selected per segment under the ADF rule.
5. The feature-level statistic $\hat T_j$ is computed across the admissible partition.
6. Stationary-bootstrap inference is conducted under fixed boundaries.
7. Selected operators are recorded in an anonymised frozen-operator registry.

Regime construction is a retrospective in-sample characterisation. Downstream operator use is separate, under train-only freezing, causal alignment, and sealed evaluation.

## Scope of inference

The test is conditional on the supplied boundaries. The volatility-state partition is treated as an input to the operator-stability test, not as an object jointly estimated with $d^{*}$. Boundary sensitivity and joint uncertainty are reserved for the manuscript in progress.

Caveats:

- $d^{*}$ is grid-valued; $\hat T_j$ inherits the grid resolution.
- The bootstrap resamples independently within segments; changepoint uncertainty is not propagated.
- Per-feature tests are reported. No multiplicity adjustment is applied.

## Public registry schema

`results/frozen_operators.csv` contains the following anonymised fields:

```text
feature_id, feature_class, scope, window_id, window_order,
d_star, adf_rejects, operator_status,
bootstrap_p_value_bucket, used_for_operator_selection, n_obs_bin
```

This file is a publication registry, not an operational registry.

## Missing-data policy

The default is `fill_method=None`. Missing observations remain in the indexed series; FFD windows containing missing values are not transformed. The output index is aligned with the input index by timestamp.

Forward fill (`fill_method="ffill"`) is available only as an explicit sensitivity specification. It is not the baseline.

## Repository structure

```text
d-invariance-ffd/
├── README.md
├── src/
├── notebooks/
├── docs/
├── config/
├── results/
├── tests/
└── paper/
```

## Installation

With Conda:

```bash
conda env create -f environment.yml
conda activate d-invariance-ffd
```

Otherwise:

```bash
pip install -r requirements.txt
```

## Documentation

- `docs/public_api.md` — public-safe module interface.
- `docs/methodology.md` — formal hypothesis, test statistic, and bootstrap procedure.
- `docs/research_mapping.md` — mapping between the research design and source code.

The public source code exposes methodology utilities only. It excludes private data, private feature names, raw paths, empirical calibration values, forecasting target logic, and out-of-sample model code.

## Synthetic example

`examples/synthetic_d_invariance.py` demonstrates segment construction, $d^{*}$ selection, and the d-invariance statistic without private data or empirical calibration.

## Confidentiality

The manuscript, private notebooks, raw data, feature-name decoder, and calibration files are confidential and are not part of the public repository. The public repository releases only anonymised derived artefacts suitable for methodological review.

## Status

The compendium is under preparation. The current release is intended for methodological review and reproducibility support, not for trading replication.

## Citation

A `CITATION.cff` file will be provided before public release.

## License

Code: Apache 2.0.
Documentation and public manuscript material: CC BY 4.0 unless otherwise stated.
Private data, private notebooks, and confidential manuscript drafts are excluded.
