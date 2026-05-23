# Testing the d-Invariance Hypothesis for the Fixed-Width Fractional Differencing Operator Across Volatility States Using VIX

**Author:** T. Niero

## Overview

This repository is a research compendium for testing whether the fixed-width fractional differencing (FFD) operator remains stable across volatility states defined from VIX. The central object of inference is the stability of a preprocessing operator, not the estimation of a latent long-memory parameter.

The repository documents a regime-conditioned workflow that combines structural-break detection, nonparametric segmentation, feature-level FFD estimation, and stationary bootstrap-based d-invariance testing. Downstream predictive evaluation is included only as supporting material under a train-only frozen-operator protocol and a sealed out-of-sample design.

## Research Question

Does the minimum stationarity-inducing fixed-width fractional differencing order (FFD) d remain invariant across VIX-conditioned volatility states and nonparametric sub-segments when the FFD operator specification is held fixed?

In this repository, “fixed operator specification” means that the FFD implementation, truncation rule, candidate grid, and stationarity-selection rule are held constant across windows; only the data subset changes. The question is therefore about the stability of the selected preprocessing order across states, not about time variation in an ARFIMA memory parameter.

## Formal Hypothesis

For each feature, the null hypothesis is that the minimum admissible fixed-width fractional differencing order remains constant across the segments induced by the volatility-state partition. The corresponding test statistic is the maximum pairwise absolute difference between segment-specific selected orders.

The mathematical statement is provided in `docs/methodology.md`.

Inference is conducted by bootstrap under fixed train-segment boundaries. The public repository reports anonymised registry outputs and bucketed bootstrap evidence only; raw p-values and private calibration settings are excluded from release.

## Methodological Design

The public pipeline is organised as follows:

1. Construction of VIX-conditioned volatility regimes from structural-break diagnostics.
2. Nonparametric method NP-MOJO segmentation within regime partitions.
3. Application of the fixed-width fractional differencing operator.
4. Selection of the minimum admissible d under an ADF-based stationarity rule.
5. Feature-level testing of the d-invariance hypothesis across windows.
6. Bootstrap-based inference.
7. Publication of an anonymised frozen-operator registry.

The structural-break layer uses VIX as an external volatility proxy and treats regime construction as retrospective in-sample characterisation. Any downstream use of selected operators is kept separate from this layer and is conducted under train-only freezing, causal feature alignment, and sealed evaluation, in order to preserve the distinction between descriptive regime analysis and predictive use. 

## Scope

The public repository includes method code, public-safe notebooks, documentation, configuration templates, reproducibility scaffolding, and an anonymised `results/frozen_operators.csv`. It excludes raw licensed data, feature names, feature-class decoders, vendor identifiers, exact calibration schedules, raw p-values, raw or transformed feature matrices, and operational out-of-sample signal outputs.

## Public Registry Schema

The public file `results/frozen_operators.csv` contains only anonymised fields:

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

This file is a publication registry rather than a private operational registry. Its purpose is to document operator-selection outcomes without revealing the proprietary feature universe, licensed inputs, or confidential calibration details.


## Repository Structure

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

Create the environment with Conda:

```bash
conda env create -f environment.yml
conda activate d-invariance-ffd
```

If Conda is unavailable:

```bash
pip install -r requirements.txt
```

## Getting Started

1. Read `docs/disclosure_policy.md` before adding files to the public repository.
2. Use `notebooks/00_data_provenance.ipynb` to verify input provenance and environment setup.
3. Run the public workflow in sequence: break detection, segmentation, FFD estimation, and d-invariance testing.
4. Treat `results/frozen_operators.csv` as a publication artifact only, not as the private operational registry. 

## Confidentiality Boundary

The manuscript, private notebooks, raw data, feature-name decoder, and calibration files are confidential and are not part of the public repository. The public repository documents the method and releases only anonymised derived artefacts suitable for methodological review.

The public repository documents the method and publishes only anonymised derived artefacts.

## Disclosure Rule

The governing disclosure rule is: release the methodology; protect the signal. Public artefacts should support review of the procedure without disclosing licensed data, the exact feature universe, or confidential calibration details.

## Status

This research compendium is under preparation. The current release is intended for methodological review and reproducibility support rather than for trading replication. 

## Citation

A `CITATION.cff` file will be provided before public release. 

## License

Code: Apache 2.0.  
Documentation and public manuscript material: CC BY 4.0 unless otherwise stated.  
Private data, private notebooks, and confidential manuscript drafts are excluded. 

## Public API

The reusable public modules are documented here:

- `docs/public_api.md` — public-safe module interface.
- `docs/research_mapping.md` — mapping between the research design and source code.

The public source code exposes methodology utilities only. It does not include private data, private feature names, raw paths, empirical calibration values, forecasting target logic, or OOS model code.

## Synthetic Example

A public-safe synthetic example is available at `examples/synthetic_d_invariance.py`.
It demonstrates segment construction, `d*` estimation, and the d-invariance statistic without private data or empirical calibration.
