# Methodology

## Scope

This document presents the formal methodological description of the public d-invariance pipeline. The object of inference is the stability of the fixed-width fractional differencing operator across volatility-conditioned segments, not the estimation of a latent ARFIMA memory parameter and not the direct optimisation of a trading rule.

The public release is designed for methodological review and reproducibility support. It excludes raw licensed data, proprietary feature identifiers, exact private calibration schedules, and operational signal outputs.

## Research Object

Let $X^{(j)}_t$ denote feature $j$ observed at time $t$. The purpose of the pipeline is to determine whether the minimum admissible fixed-width fractional differencing order required to satisfy a stationarity rule remains stable across segments induced by volatility-state partitioning and within-regime segmentation.

The inferential target is therefore a preprocessing operator. The analysis does not interpret the selected differencing order as a direct estimate of an underlying structural long-memory parameter. Rather, it treats the selected order as an operational transformation choice produced by a fixed estimation rule.

## Pipeline Overview

The public pipeline is organised in seven stages:

1. Construction of VIX-conditioned volatility regimes from structural-break diagnostics.
2. Nonparametric segmentation within regimes using NP-MOJO.
3. Application of the fixed-width fractional differencing operator.
4. Selection of the minimum admissible $d^*$ under an ADF-based stationarity rule.
5. Feature-level testing of the d-invariance hypothesis across windows.
6. Bootstrap-based inference.
7. Publication of an anonymised frozen-operator registry.

The regime-construction layer is retrospective and in-sample. Any downstream predictive use is separated from this stage and is carried out under train-only operator freezing, causal feature alignment, and sealed evaluation.

## Regime Construction

Volatility states are constructed from VIX-based structural-break diagnostics. In the public pipeline, VIX is treated as an external volatility proxy used to partition the sample into broad volatility regimes before within-regime segmentation.

This stage is descriptive rather than predictive. Its role is to define windows within which the stability of the selected fixed-width fractional differencing order can be examined.

## Within-Regime Segmentation

Within each volatility regime, the series is further partitioned by a nonparametric segmentation procedure based on NP-MOJO. This step refines the regime partition by allowing additional distributional and dependence changes to be detected without imposing a restrictive parametric form.

The resulting segments define the local windows on which feature-level admissible differencing orders are estimated.

## Fixed-Width Fractional Differencing

For each feature $j$, the series is transformed by a fixed-width fractional differencing operator parameterised by $d$. The operator is used as a preprocessing device intended to reduce non-stationarity while preserving as much memory as possible under a fixed admissibility rule.

The public repository exposes the operator construction, but not the confidential operational calibration values beyond the release boundary defined in the disclosure policy.

## Minimum Admissible Order Selection

For each feature and each admissible window, a grid of candidate values of $d$ is evaluated under a fixed stationarity-selection rule. The selected value $d^*$ is the minimum admissible order satisfying the configured ADF-based criterion.

Formally, for feature $j$ in segment $k$, let $d^{*}_{j,k}$ denote the selected minimum admissible differencing order. This quantity is not interpreted as a structural memory estimate; it is the output of a predefined transformation-selection rule.

## Formal Hypothesis

For each feature $j$, let $d^{*}_{j,k}$ denote the minimum admissible fixed-width fractional differencing order estimated on segment $k$, for $k = 1, \dots, K$.

The feature-level null hypothesis of segmental invariance is

```math
H_{0,j}: d^{*}_{j,1} = d^{*}_{j,2} = \cdots = d^{*}_{j,K}.
```

The alternative is that at least one segment-specific selected order differs:

```math
H_{A,j}: \exists\, k \neq l \text{ such that } d^{*}_{j,k} \neq d^{*}_{j,l}.
```

This hypothesis is formulated at the feature level. The purpose is to determine whether the transformation rule yields a stable selected order across the segmentation induced by volatility states and within-regime change points.

## Test Statistic

For each feature $j$, the observed dispersion in selected orders across segments is summarised by the maximum pairwise absolute difference:

```math
T_j = \max_{1 \leq k < l \leq K} \left| d^{*}_{j,k} - d^{*}_{j,l} \right|.
```

A value of $T_j = 0$ implies exact equality of the selected orders across all observed segments. Larger values indicate stronger departures from d-invariance.

This statistic is intentionally nonparametric in form. It measures the extremal disagreement among segment-specific selected orders and does not impose a linear or Gaussian structure on the segment-level deviations.

## Bootstrap Inference

Inference is conducted by bootstrap under fixed train-segment boundaries. The bootstrap layer is designed to approximate the sampling variability of the selected orders under the null of segmental invariance while respecting the segmentation structure used in estimation.

At the public-release level, the repository reports only anonymised registry outputs and bucketed bootstrap evidence. Raw p-values, exact private bootstrap schedules, and confidential calibration settings are excluded from release.

## Interpretation

Failure to reject $H_{0,j}$ is interpreted as absence of evidence against stability of the selected FFD order for feature $j$ across the observed segments. Rejection of $H_{0,j}$ is interpreted as evidence that the admissible preprocessing order is segment-dependent.

This interpretation is operational rather than structural. A rejection does not by itself establish a specific economic mechanism; it establishes instability of the selected preprocessing rule under the imposed segmentation and stationarity protocol.

## Non-Claims

This pipeline does not claim to estimate the true fractional integration parameter of the data-generating process. It does not claim that a rejection of d-invariance identifies a specific economic mechanism. It does not claim to publish or replicate a trading signal.

The claim is narrower: under a fixed FFD selection rule and fixed volatility-conditioned segmentation, the selected preprocessing order may or may not remain stable across windows.


## Public Registry

The public file `results/frozen_operators.csv` is a publication registry rather than a private operational registry. It documents selected operator outcomes in anonymised form without disclosing the proprietary feature universe, raw vendor data, or confidential private calibrations.

The public schema is restricted to fields such as:

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

`feature_class` reports the transformation class, such as `LOG_LEVEL` or `LEVEL`. It does not report the economic asset class, country, ticker, maturity, or signal role.

## Reproducibility Boundary

The public repository is intended to make the procedure auditable and reproducible at the methodological level. Reproducibility here means that an independent reviewer can inspect the operator definition, segmentation logic, test design, and disclosure structure, even when raw licensed inputs and private operational details cannot be released.

