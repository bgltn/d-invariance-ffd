# Testing the d-Invariance Hypothesis for the Fixed-Width Fractional Differencing Operator Across Volatility States Using VIX

**Author:** T. Niero

## Overview

This repository is a research compendium for testing whether the fixed-width fractional differencing (FFD) order selected under a stationarity criterion remains stable across VIX-defined volatility states and nonparametric sub-segments. The object of inference is the stability of a preprocessing operator, not the profitability of a trading strategy. 

## Question

Does the selected FFD threshold d remain invariant across volatility-conditioned regimes when the operator specification is held fixed? This differs from ARFIMA inference: here, d is a preprocessing hyperparameter chosen before downstream modeling, rather than a latent structural parameter of the data-generating process. 
## Formal Hypothesis

For each feature \(j\), let \(d^*_{j,k}\) denote the minimum FFD order selected inside segment \(k\).

The feature-level null hypothesis is:

\[
H_{0,j}: d^*_{j,1} = d^*_{j,2} = \cdots = d^*_{j,K}.
\]

The observed statistic is:

\[
T_j = \max_{k<l} |d^*_{j,k} - d^*_{j,l}|.
\]

Stationary-bootstrap p-value buckets are reported in the public registry. Raw p-values and private bootstrap settings are not released.

## Method

The public pipeline contains: fixed-width fractional differencing, ADF-based minimum d selection, VIX-based regime construction, NP-MOJO segmentation, feature-level d-invariance testing, stationary-bootstrap inference, and an anonymised frozen-operator registry. The notebook and publication strategy both enforce train-only operator freezing, sealed downstream evaluation, and audit-only bootstrap diagnostics. 


## Scope

Included: method code, public-safe notebooks, documentation, configuration templates, reproducibility scaffolding, and an anonymised `results/frozen_operators.csv`. Excluded: raw licensed data, feature names, feature-class decoders, vendor identifiers, exact calibration schedules, raw p-values, raw or transformed feature matrices, and operational out-of-sample signal outputs. 

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

## Structure

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

## Install

```bash
conda env create -f environment.yml
conda activate d-invariance-ffd
```

If Conda is unavailable:

```bash
pip install -r requirements.txt
```

## Getting started

1. Read `docs/disclosure_policy.md` before adding files to the public repository.
2. Use `notebooks/00_data_provenance.ipynb` to verify input provenance and environment setup.
3. Run the public workflow in order: break detection, segmentation, FFD estimation, and d-invariance testing.
4. Treat `results/frozen_operators.csv` as a publication registry only, not as the private operational registry. 

## Confidentiality Boundary

The manuscript, private notebooks, raw data, feature-name decoder, and calibration files are confidential. They are not part of the public repository.

The public repository documents the method and publishes only anonymised derived artefacts.

## Disclosure rule

Release the methodology; protect the signal. Public artifacts must support review of the procedure without revealing licensed data, the exact feature universe, or private calibration details. 

## Status

Research compendium under preparation.
The current release is intended for methodological review, not for trading replication.

## Citation

A `CITATION.cff` file will be provided before public release.

## Licence

Code: Apache 2.0.  
Documentation and public manuscript material: CC BY 4.0 unless otherwise stated.  
Private data, private notebooks, and confidential manuscript drafts are excluded.
