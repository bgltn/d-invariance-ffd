# Methodology

## Scope

This document presents the formal methodological description of the public d-invariance pipeline. The object of inference is the stability of the Fixed-width Fractional Differencing operator across fixed admissible partitions, not the estimation of a latent ARFIMA memory parameter and not the direct optimisation of a trading rule.

The public release is designed for methodological review and reproducibility support. It excludes raw licensed data, proprietary feature identifiers, exact private calibration schedules, forecasting logic, trading rules, and operational signal outputs.

## Standard glossary

| Term | Definition |
|---|---|
| $d$ | Fractional differencing order. It is a parameter of the Fixed-width Fractional Differencing operator. In this repository, it is evaluated on a finite admissible grid $\mathcal{D}$. |
| $d^*$ | Minimum admissible value on the grid $\mathcal{D}$ such that the ADF test rejects the unit-root null at level $\alpha$ on the FFD-transformed series. |
| FFD operator | Fixed-width fractional differencing operator with truncation threshold $\tau$, applied to one univariate series. |
| Regime | Contiguous time interval delimited by structural breaks detected on the VIX series. Regimes are the parent partition. They are exogenous to the feature being tested. |
| Volatility state | Contiguous time interval inside one regime, delimited by changepoints detected by NP-MOJO. Volatility states are the child partition. |
| Segment | Synonym for volatility state when referring to child windows used for local operator estimation. |
| Admissible partition | Either the parent regime partition or a volatility-state partition nested inside a fixed parent regime partition. The d-invariance test is conditional on one admissible partition. |
| d-invariance hypothesis | Null hypothesis that the selected order $d^*$ is equal across the $K$ units of one admissible partition, with the FFD operator specification held fixed. |

## Research Object

Let $X^{(j)}_t$ denote feature $j$ observed at time $t$. The purpose of the pipeline is to test whether the selected minimum stationarity-inducing FFD order remains stable across the units of a fixed admissible partition.

The inferential target is a preprocessing operator. The analysis does not interpret the selected differencing order as a direct estimate of an underlying structural long-memory parameter. Rather, it treats the selected order as an operational transformation choice produced by a fixed estimation rule.

## Boundary Hierarchy

The repository uses a two-level boundary hierarchy.

First, VIX structural-break analysis defines parent regimes. These regimes are contiguous, ordered, and non-overlapping.

Second, NP-MOJO segmentation may be applied inside each parent regime. These child windows are called volatility states or segments.

A volatility state must lie inside one regime. A volatility state cannot cross a regime boundary.

The hierarchy is:

```text
VIX-defined regime
  -> NP-MOJO volatility state
```

The d-invariance test can be applied to either admissible partition:

```text
parent regime partition
child volatility-state partition nested inside a fixed regime partition
```

The test is always conditional on the partition supplied to it.

## Pipeline Overview

The public pipeline is organised in seven stages:

1. Construction of VIX-defined regimes from structural-break diagnostics on VIX.
2. Construction of NP-MOJO volatility-state segments inside each VIX-defined regime.
3. Application of the Fixed-width Fractional Differencing operator.
4. Selection of the minimum admissible $d^*$ under an ADF-based stationarity rule.
5. Feature-level testing of the d-invariance hypothesis across the units of one admissible partition.
6. Stationary-bootstrap inference conditional on fixed boundaries.
7. Optional publication of an anonymised frozen-operator registry.

The regime-construction layer is retrospective and in-sample. Any downstream predictive use is separated from this stage and is carried out under train-only operator freezing, causal feature alignment, and sealed evaluation.

## Regime Construction

Regimes are constructed from VIX-based structural-break diagnostics.

In the public methodology, VIX is treated as an external volatility proxy used to partition the training sample into broad parent regimes. These regimes are not estimated from the feature being tested.

This stage is descriptive rather than predictive. Its role is to define parent windows within which the stability of the selected Fixed-width Fractional Differencing order can be examined.

## Within-Regime Segmentation

Within each VIX-defined regime, NP-MOJO may be used to define child volatility-state segments.

NP-MOJO is a nonparametric segmentation method designed to detect changepoints in marginal distributions and nonlinear serial dependence without pre-specifying the type of change. In this project, NP-MOJO is an upstream segmentation method. It produces boundaries. The FFD layer consumes those boundaries.

The resulting volatility-state segments define local windows on which feature-level admissible differencing orders are estimated.

## Fixed-Width Fractional Differencing

For each feature $j$, the series is transformed by a Fixed-width Fractional Differencing operator parameterised by $d$.

The operator is used as a preprocessing device intended to reduce non-stationarity while preserving dependence structure under a fixed admissibility rule.

The public repository exposes the operator construction. It does not expose confidential operational calibration values beyond the release boundary defined in the disclosure policy.

## Minimum Admissible Order Selection

For each feature and each admissible window, a finite grid of candidate values of $d$ is evaluated under a fixed stationarity-selection rule.

The selected value $d^*$ is the minimum admissible order satisfying the configured ADF-based criterion.

Formally, for feature $j$ in segment $k$, let $\widehat d^{*}_{j,k}$ denote the estimated selected order. This quantity is not interpreted as a structural memory estimate. It is the output of a predefined transformation-selection rule.

The tuple $(\mathcal{D}, \tau, \alpha, \text{ADF parameters})$ is held fixed across segments for a given test.

## Test of the $d^*$-Invariance Hypothesis

Let $\mathcal{P} = \{S_1,\ldots,S_K\}$ be a fixed admissible partition of the training period. Each $S_k$ is either a VIX-defined regime or an NP-MOJO volatility state nested inside one regime.

Let $\mathcal{D}$ denote the finite grid of candidate orders, $\tau$ the FFD truncation threshold, and $\alpha$ the ADF significance level.

Hold $(\mathcal{D}, \tau, \alpha, \text{ADF parameters})$ fixed across segments.

For feature $j$, let $\widehat d^{*}_{j,k}$ be the minimum value $d \in \mathcal{D}$ for which the ADF test rejects the unit-root null at level $\alpha$ on the FFD-transformed series in segment $S_k$.

The null hypothesis, conditional on $\mathcal{P}$, is:

```math
H_{0,j}: d^{*}_{j,1} = d^{*}_{j,2} = \cdots = d^{*}_{j,K}.
```

The alternative is:

```math
H_{A,j}: \exists\, k \neq l \text{ such that } d^{*}_{j,k} \neq d^{*}_{j,l}.
```

The observed instability statistic is:

```math
\widehat T_j
=
\max_{1 \leq k < l \leq K}
\left|
\widehat d^{*}_{j,k}
-
\widehat d^{*}_{j,l}
\right|.
```

The statistic measures the largest observed pairwise discrepancy in the selected FFD order across the fixed units of one admissible partition.

## Stationary-Bootstrap Calibration

Bootstrap inference is applied conditionally on the fixed upstream partition.

For $b = 1,\ldots,B$:

1. Independently inside each segment $S_k$, draw a stationary-bootstrap sample of length $n_k$.
2. Use mean block length $L_k = 1.5\,n_k^{1/3}$.
3. Re-estimate $d^{*(b)}_{j,k}$ on each bootstrap sample using the fixed operator specification.
4. Compute the recentred bootstrap statistic:

```math
T^{*(b)}_j
=
\max_{k<l}
\left|
\left(d^{*(b)}_{j,k} - \widehat d^{*}_{j,k}\right)
-
\left(d^{*(b)}_{j,l} - \widehat d^{*}_{j,l}\right)
\right|.
```

The bootstrap p-value is:

```math
\widehat p_j
=
\frac{
1 + \sum_{b=1}^{B}\mathbf{1}\{T^{*(b)}_j \geq \widehat T_j\}
}{
1 + B
}.
```

Reject $H_{0,j}$ at level $\alpha$ if:

```math
\widehat p_j < \alpha.
```

## Scope and Limitations

The test is conditional on the fixed partition $\mathcal{P}$.

Boundary uncertainty is not propagated. The bootstrap does not re-estimate VIX structural breaks. The bootstrap does not re-run NP-MOJO. Segment boundaries remain fixed during resampling.

The stationary bootstrap is applied independently within each segment.

The selected order $\widehat d^{*}_{j,k}$ is grid-valued. Therefore, $\widehat T_j$ and $T^{*(b)}_j$ inherit the grid resolution.

Per-feature tests are reported. Multiplicity adjustment for joint conclusions across features is not part of this test.

The public repository exposes the test design. It does not expose private calibration schedules, raw bootstrap p-values, exact bootstrap seeds, private feature names, private feature maps, or empirical results reserved for the research manuscript.

## Interpretation

Failure to reject $H_{0,j}$ is interpreted as absence of evidence against stability of the selected FFD order for feature $j$ across the supplied admissible partition.

Rejection of $H_{0,j}$ is interpreted as evidence that the admissible preprocessing order is segment-dependent.

This interpretation is operational rather than structural. A rejection does not by itself establish a specific economic mechanism. It establishes instability of the selected preprocessing rule under the imposed segmentation and stationarity protocol.

## Non-Claims

This pipeline does not claim to estimate the true fractional integration parameter of the data-generating process.

It does not claim that a rejection of d-invariance identifies a specific economic mechanism.

It does not claim to publish or replicate a trading signal.

The claim is narrower: under a fixed FFD selection rule and a fixed admissible partition, the selected preprocessing order may or may not remain stable across windows.

## Public Registry

A public-safe frozen-operator registry may be released as a publication registry rather than as a private operational registry.

When released, it documents selected operator outcomes in anonymised form without disclosing the proprietary feature universe, raw vendor data, or confidential private calibrations.

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

`feature_class` reports the transformation class, such as `LOG_LEVEL` or `LEVEL`. It does not report the economic asset class, country, ticker, maturity, vendor identifier, or signal role.

## Reproducibility Boundary

The public repository is intended to make the procedure auditable and reproducible at the methodological level.

Reproducibility here means that an independent reviewer can inspect the operator definition, boundary contract, segmentation role, test design, and disclosure structure, even when raw licensed inputs and private operational details cannot be released.

## References

- Dickey, D. A., and Fuller, W. A. (1979). Distribution of the estimators for autoregressive time series with a unit root. *Journal of the American Statistical Association*, 74(366), 427-431.
- López de Prado, M. (2018). *Advances in Financial Machine Learning*. Wiley.
- McGonigle, E. T., and Cho, H. (2025). Nonparametric data segmentation in multivariate time series via joint characteristic functions. *Biometrika*, 112(2), asaf024.
- Politis, D. N., and Romano, J. P. (1994). The stationary bootstrap. *Journal of the American Statistical Association*, 89(428), 1303-1313.
