# Research-to-Code Mapping

This document maps the public source modules to the research design.

The repository exposes methodology utilities only. Empirical calibration, private feature names, raw data paths, forecasting target logic, and OOS model code remain outside the public package.

## Research object

The study tests whether the fixed-width fractional differencing order `d*` is invariant across volatility-conditioned estimation windows.

The object of inference is the preprocessing operator, not a downstream forecasting model.

## Module mapping

| Research component | Public module | Role |
|---|---|---|
| Fixed-width fractional differencing | `ffd.operator` | Builds FFD weights and applies the transform |
| Minimum admissible `d*` | `ffd.estimator` | Selects the first `d` satisfying the ADF rule |
| d-invariance statistic | `ffd.invariance` | Computes maximum pairwise `d*` displacement across windows |
| Segment boundaries | `segmentation.boundaries` | Validates externally supplied non-overlapping windows |
| Frozen operator registry | `audit.schema` | Validates anonymised publication artefacts |
| Public-safety check | `audit.leakage` | Scans files for caller-supplied forbidden strings |

## Boundary hierarchy

The pipeline uses a two-level boundary hierarchy.

1. **Parent volatility regimes**  
   Volatility-state regimes are defined outside the FFD operator-selection step. These regimes provide the parent estimation windows.

2. **Within-regime segmentation**  
   Nonparametric segmentation is applied inside each parent regime. Segment boundaries are not allowed to cross parent-regime boundaries.

3. **Operator selection**  
   The selected order \(d^*\) is estimated independently inside each admissible train segment. The FFD transformation never crosses a regime or segment boundary.

The d-invariance test is therefore conditional on this boundary hierarchy. If a segmentation method proposes a boundary outside a parent regime, that boundary is rejected by construction. If different segmentation methods imply different admissible partitions, they define different conditional tests.

## Segmentation boundary convention

The public code does not implement NP-MOJO calibration.

It accepts externally supplied boundary dates and converts them into non-overlapping windows.

A boundary date is interpreted as the first observation of the new segment.

## d-invariance statistic

For feature `j`, with selected orders across `K` windows:

```text
T_j = max_{k < l} |d*_{j,k} - d*_{j,l}|
