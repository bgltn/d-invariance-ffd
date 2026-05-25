# Methodology

## Scope

This document is the formal methodological description of the public d-invariance pipeline. The object of inference is the stability of the fixed-width fractional differencing (FFD) operator across fixed admissible partitions. It is not the estimation of a latent long-memory parameter and not the direct optimisation of a trading rule.

The public release supports methodological review and reproducibility. It excludes raw licensed data, proprietary feature identifiers, exact private calibration schedules, forecasting logic, and operational signal outputs.

## Standard glossary

| Term | Definition |
|---|---|
| $`d`$ | Fractional differencing order. A parameter of the FFD operator, evaluated on a finite grid $`\mathcal{D}`$. |
| $`d^{\ast}`$ | Minimum value $`d \in \mathcal{D}`$ such that the augmented Dickey–Fuller (ADF) test rejects the unit-root null at level $`\alpha`$ on the FFD-transformed series. |
| FFD operator | Fixed-width fractional differencing operator with truncation threshold $`\tau`$, applied to one univariate series. |
| **Regime** | Contiguous time interval delimited by structural breaks detected on the VIX series. Parent partition. Exogenous to the feature under test. |
| **Volatility state** (segment) | Contiguous time interval inside one regime, delimited by change points detected by NP-MOJO. Child partition. |
| Admissible partition | Either the parent regime partition or a volatility-state partition nested in a fixed regime. The test is conditional on one admissible partition. |
| d-invariance hypothesis | Null hypothesis that the selected order $`d^{\ast}`$ is equal across the $`K`$ units of one admissible partition, with the FFD operator specification held fixed. |

The hypothesis is stated at the level of the selected order $`d^{\ast}`$, not the operator parameter $`d`$. The two are distinct objects: $`d`$ is a parameter of the operator; $`d^{\ast}`$ is the data-dependent quantity produced by a fixed selection rule.

## Research object

Let $`X^{(j)}_t`$ denote feature $`j`$ at time $`t`$. The pipeline tests whether the selected minimum stationarity-inducing FFD order remains stable across the units of a fixed admissible partition.

The inferential target is a preprocessing operator. The analysis does not interpret $`d^{\ast}`$ as a structural long-memory parameter. It treats $`d^{\ast}`$ as the output of a predefined transformation-selection rule.

## Boundary hierarchy

The pipeline uses a two-level boundary hierarchy.

First, structural-break analysis on VIX defines parent regimes. Regimes are contiguous, ordered, and non-overlapping.

Second, NP-MOJO segmentation may be applied inside each regime. The resulting child windows are called volatility states or segments. A volatility state lies inside one regime and cannot cross a regime boundary.

```text
VIX-defined regime  (parent)
  └── NP-MOJO volatility state  (child)
```

The d-invariance test can be applied to either admissible partition: the parent regime partition, or a child volatility-state partition inside one fixed regime. The test is always conditional on the partition supplied to it.

## Pipeline overview

The public pipeline is organised in seven stages:

1. Structural-break detection on VIX defines the parent regimes.
2. NP-MOJO segmentation within each regime defines the child volatility states.
3. The FFD operator is applied with fixed specification.
4. The minimum admissible order $d^{*}$ is selected per segment under the ADF rule.
5. The feature-level statistic $\hat{T}_j$ is computed across the admissible partition.
6. Stationary-bootstrap inference is conducted under fixed boundaries.
7. Selected operators may be recorded in an anonymised frozen-operator registry.

Regime construction is retrospective in-sample characterisation. Downstream predictive use is separate, under train-only operator freezing, causal feature alignment, and sealed evaluation.

## Regime construction

Regimes are constructed from structural-break diagnostics on VIX. VIX is treated as an external volatility proxy used to partition the training sample into parent regimes. Regimes are not estimated from the feature under test.

This stage is descriptive. Its role is to define parent windows within which $`d^{\ast}`$ stability is examined.

## Within-regime segmentation

Inside each regime, NP-MOJO may be applied to define child volatility states. NP-MOJO is a nonparametric segmentation method that detects change points in marginal distributions and nonlinear serial dependence without pre-specifying the type of change (McGonigle and Cho, 2025).

NP-MOJO is upstream to the FFD layer: it produces boundaries, which the FFD layer consumes. The resulting volatility states define local windows on which segment-specific selected orders are computed.

## Fixed-width fractional differencing

For each feature $`j`$, the series is transformed by an FFD operator with parameter $`d`$. The operator is a preprocessing device intended to reduce non-stationarity while preserving long-range dependence under a fixed admissibility rule (López de Prado, 2018, Chapter 5).

The implementation follows the fixed-width specification with truncation threshold $`\tau`$, producing finite impulse-response weights. Weights are applied per segment; the FFD operator is never applied across an admissible partition boundary.

## Selection of $d^{\ast}$

For each feature and each admissible segment, the candidate grid $`\mathcal{D}`$ is searched. The selected order $`d^{\ast}`$ is the smallest value $`d \in \mathcal{D}`$ for which the ADF test rejects the unit-root null at level $`\alpha`$ on the FFD-transformed series.

The ADF specification follows López de Prado (2018, snippet 5.4):

- regression: constant only (`regression="c"`);
- lag order: fixed at one (`maxlag=1`, `autolag=None`).

A minimum number of observations per segment (`min_obs`) is required before the ADF test is conducted; segments shorter than this threshold yield `status="INSUFFICIENT_OBS"` and no admissible $`d^{\ast}`$. The choice of `min_obs` follows the practical guidance in López de Prado (2018, Chapter 5), which highlights that fixed-width fractional differencing reduces the effective sample length and that the ADF test requires a sample large enough to detect rejection at the configured level. The research run uses a value calibrated to that guidance and is held constant across segments for a given test. The synthetic example uses a smaller value appropriate to the shorter synthetic series.

The tuple $`(\mathcal{D}, \tau, \alpha, \text{ADF parameters})`$ is held fixed across segments for a given test. For feature $`j`$ in segment $`k`$, $`\hat{d}^{\ast}_{j,k}`$ denotes the segment-specific selected order.

## Test of the $d^{\ast}$-invariance hypothesis

Let $`\mathcal{P} = \{S_1, \ldots, S_K\}`$ be a fixed admissible partition of the training period. Each $`S_k`$ is either a VIX-defined regime or an NP-MOJO volatility state nested in one regime.

For feature $`j`$, let $`\hat{d}^{\ast}_{j,k}`$ be the minimum value $`d \in \mathcal{D}`$ for which the ADF test rejects the unit-root null at level $`\alpha`$ on the FFD-transformed series in segment $`S_k`$.

The null hypothesis, conditional on $`\mathcal{P}`$, is:

```math
H_{0,j}: \quad d^{\ast}_{j,1} = d^{\ast}_{j,2} = \cdots = d^{\ast}_{j,K}.
```

The alternative is:

```math
H_{A,j}: \quad \exists\ 1 \le k < l \le K \ \text{such that}\ d^{\ast}_{j,k} \neq d^{\ast}_{j,l}.
```

The observed test statistic is the maximum pairwise absolute difference between segment-specific selected orders:

```math
\hat{T}_j = \max_{1 \le k \lt l \le K} \bigl| \hat{d}^{\ast}_{j,k} - \hat{d}^{\ast}_{j,l} \bigr|.
```

## Stationary-bootstrap inference

Inference is conducted by stationary bootstrap (Politis and Romano, 1994), conditional on the fixed admissible partition.

For $`b = 1, \ldots, B`$:

1. Independently in each segment $`S_k`$, draw a stationary-bootstrap sample of length $`n_k`$ with mean block length $`L_k`$, using circular random-length blocks.
2. Re-estimate $`d^{\ast(b)}_{j,k}`$ on each bootstrap sample using the same fixed operator specification.
3. Compute the recentred bootstrap statistic:

```math
T^{\ast(b)}_j = \max_{1 \le k \lt l \le K} \bigl| (d^{\ast(b)}_{j,k} - \hat{d}^{\ast}_{j,k}) - (d^{\ast(b)}_{j,l} - \hat{d}^{\ast}_{j,l}) \bigr|.
```

The mean block length is set segment-wise as:

```math
L_k = \mathrm{clip}\bigl(1.5\, n_k^{1/3},\ 1,\ n_k\bigr).
```

The clipping ensures $`L_k \in [1, n_k]`$. The cube-root rule is the operational convention used in this project. It is not claimed as universally optimal; Politis and White (2004) provide an automatic alternative reserved for sensitivity analysis.

Recentring around $`\hat{d}^{\ast}_{j,k}`$ calibrates the bootstrap to the null distribution of $`\hat{T}_j`$. Without recentring, the bootstrap mimics the alternative and the test loses size control.

The bootstrap p-value is:

```math
\hat{p}_j = \frac{1 + \sum_{b=1}^{B} \mathbf{1}\{T^{\ast(b)}_j \ge \hat{T}_j\}}{1 + B}.
```

The decision rule rejects $`H_{0,j}`$ at level $`\alpha`$ if $`\hat{p}_j < \alpha`$.

## Scope and limitations

The test is conditional on the fixed admissible partition $`\mathcal{P}`$.

Boundary uncertainty is not propagated. The bootstrap does not re-estimate VIX structural breaks. The bootstrap does not re-run NP-MOJO. Segment boundaries remain fixed during resampling.

Resampling is independent within segments. Under the null, this is innocuous; under boundary misspecification, the test conflates operator instability with partition misspecification.

The selected order $`\hat{d}^{\ast}_{j,k}`$ is grid-valued. The statistics $`\hat{T}_j`$ and $`T^{\ast(b)}_j`$ inherit the grid resolution. The bootstrap p-value is therefore a discrete random variable.

Per-feature tests are reported. Multiplicity adjustment for joint conclusions across features is not part of this test.

The public repository exposes the test design. It excludes private calibration schedules, raw p-values, bootstrap seeds, private feature names, private feature maps, and empirical results reserved for the research manuscript.

## Interpretation

Failure to reject $`H_{0,j}`$ is read as absence of evidence against stability of the selected FFD order for feature $`j`$ across the supplied admissible partition. Rejection of $`H_{0,j}`$ is read as evidence that the admissible preprocessing order is segment-dependent.

This interpretation is operational, not structural. A rejection does not by itself identify an economic mechanism. It establishes instability of the selected preprocessing rule under the imposed segmentation and stationarity protocol.

## Non-claims

- The pipeline does not estimate the true fractional-integration parameter of the data-generating process.
- A rejection of d-invariance does not identify a specific economic mechanism.
- The repository does not publish or replicate a trading signal.

The claim is narrower: under a fixed FFD selection rule and a fixed admissible partition, the selected preprocessing order may or may not remain stable across segments.

## Public registry

A public-safe frozen-operator registry may be released as a publication artefact, distinct from any private operational registry. When released, it documents selected operator outcomes in anonymised form, without disclosing the proprietary feature universe, raw vendor data, or confidential calibrations.

The public schema is restricted to fields such as:

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

Field semantics are documented in `docs/disclosure_policy.md`. The `parent_regime_id` field is required for `SEGMENT` rows so that the boundary hierarchy can be reconstructed from the registry alone. The `bootstrap_p_value_bucket` field discloses one of three buckets (`p<0.01`, `0.01<=p<0.10`, `p>=0.10`); raw p-values are not released. The `n_obs_bin` field discloses bucketed sample sizes (`<200`, `200-500`, `500-1000`, `1000-2000`, `>2000`).

`feature_class` reports the transformation class (for example, `LOG_LEVEL` or `LEVEL`). It does not report the economic asset class, country, ticker, maturity, vendor identifier, or signal role.

## Reproducibility boundary

The public repository is intended to make the procedure auditable at the methodological level. An independent reviewer can inspect the operator definition, boundary contract, segmentation role, test design, and disclosure structure. Raw licensed inputs and private operational details are not released.

## References

- Dickey, D. A., and Fuller, W. A. (1979). Distribution of the estimators for autoregressive time series with a unit root. *Journal of the American Statistical Association*, 74(366), 427–431.
- López de Prado, M. (2018). *Advances in Financial Machine Learning*. Wiley. Chapter 5 (snippets 5.1, 5.3, 5.4, 5.5).
- McGonigle, E. T., and Cho, H. (2025). Nonparametric data segmentation in multivariate time series via joint characteristic functions. *Biometrika*, 112(2), asaf024.
- Politis, D. N., and Romano, J. P. (1994). The stationary bootstrap. *Journal of the American Statistical Association*, 89(428), 1303–1313.
- Politis, D. N., and White, H. (2004). Automatic block-length selection for the dependent bootstrap. *Econometric Reviews*, 23(1), 53–70.
