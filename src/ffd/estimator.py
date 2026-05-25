"""Estimate the minimum admissible fractional differencing order d*.

The ADF defaults follow López de Prado (2018), Advances in Financial Machine
Learning, Chapter 5, snippet 5.4:

    regression="c", autolag=None, maxlag=1

The default missing-data policy is no imputation (``fill_method=None``).
Forward fill is available only as an explicit user choice. This matches the
public-API and methodology documentation in the repository.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Iterable

import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import adfuller

from .operator import fracdiff_ffd, get_ffd_width


@dataclass(frozen=True)
class DStarResult:
    feature: str | None
    d_star: float | None
    tested_d: float | None
    adf_stat: float | None
    adf_pvalue: float | None
    adf_rejects: bool
    n_raw: int
    n_ffd: int
    width: int | None
    corr: float | None
    status: str

    def to_dict(self) -> dict:
        return asdict(self)


def _validate_inputs(
    d_grid: Iterable[float],
    threshold: float,
    adf_alpha: float,
    min_obs: int,
) -> list[float]:
    d_values = [float(d) for d in d_grid]

    if not d_values:
        raise ValueError("d_grid must contain at least one value.")
    if any(d < 0 for d in d_values):
        raise ValueError("d_grid values must be non-negative.")
    if any(d_values[i] > d_values[i + 1] for i in range(len(d_values) - 1)):
        raise ValueError("d_grid must be ordered ascending.")
    if threshold <= 0:
        raise ValueError("threshold must be strictly positive.")
    if not 0 < adf_alpha < 1:
        raise ValueError("adf_alpha must be in (0, 1).")
    if min_obs <= 0:
        raise ValueError("min_obs must be positive.")

    return d_values


def _clean_series(series: pd.Series, fill_method: str | None) -> pd.Series:
    x = series.astype(float).replace([np.inf, -np.inf], np.nan)

    if fill_method == "ffill":
        x = x.ffill()
    elif fill_method is not None:
        raise ValueError(
            f"Unsupported fill_method: {fill_method!r}. "
            "Allowed values are None (default) or 'ffill' (explicit)."
        )

    return x.dropna()


def _safe_corr(original: pd.Series, transformed: pd.Series) -> float | None:
    aligned = pd.concat(
        [original.reindex(transformed.index), transformed],
        axis=1,
    ).dropna()

    if len(aligned) < 2:
        return None
    if aligned.iloc[:, 0].std() == 0 or aligned.iloc[:, 1].std() == 0:
        return None

    return float(aligned.iloc[:, 0].corr(aligned.iloc[:, 1]))


def estimate_d_star(
    series: pd.Series,
    d_grid: Iterable[float],
    threshold: float,
    adf_alpha: float,
    min_obs: int,
    *,
    feature: str | None = None,
    adf_regression: str = "c",
    autolag: str | None = None,
    maxlag: int | None = 1,
    fill_method: str | None = None,
) -> DStarResult:
    """Select the minimum admissible d on a grid under an ADF stationarity rule.

    Parameters
    ----------
    series : pd.Series
        Univariate input series.
    d_grid : Iterable[float]
        Ordered, ascending grid of non-negative candidate orders.
    threshold : float
        FFD weight truncation threshold tau (> 0).
    adf_alpha : float
        ADF significance level in (0, 1).
    min_obs : int
        Minimum number of FFD observations required for the ADF test.
    feature : str | None
        Optional feature label propagated to the result.
    adf_regression : str
        ADF regression specification. Default 'c' (constant only)
        follows López de Prado (2018, snippet 5.4).
    autolag : str | None
        Information criterion for automatic lag selection. Default None
        (no auto-selection) follows López de Prado (2018, snippet 5.4).
    maxlag : int | None
        Fixed lag order for the ADF test. Default 1 follows
        López de Prado (2018, snippet 5.4).
    fill_method : str | None
        Missing-data policy. Default None means no imputation. 'ffill'
        applies forward fill and must be reported as a sensitivity choice.

    Returns
    -------
    DStarResult
        Dataclass with the selected order, ADF outcome, and status flag.
    """
    d_values = _validate_inputs(
        d_grid=d_grid,
        threshold=threshold,
        adf_alpha=adf_alpha,
        min_obs=min_obs,
    )

    x = _clean_series(series, fill_method=fill_method)

    if x.empty:
        return DStarResult(
            feature=feature,
            d_star=None,
            tested_d=None,
            adf_stat=None,
            adf_pvalue=None,
            adf_rejects=False,
            n_raw=0,
            n_ffd=0,
            width=None,
            corr=None,
            status="EMPTY_SERIES",
        )

    last_result: DStarResult | None = None

    for d in d_values:
        y = fracdiff_ffd(
            series=x,
            d=d,
            threshold=threshold,
            fill_method=None,
        )

        width = get_ffd_width(d=d, threshold=threshold)
        corr = _safe_corr(original=x, transformed=y)

        if len(y) < min_obs:
            last_result = DStarResult(
                feature=feature,
                d_star=None,
                tested_d=d,
                adf_stat=None,
                adf_pvalue=None,
                adf_rejects=False,
                n_raw=len(x),
                n_ffd=len(y),
                width=width,
                corr=corr,
                status="INSUFFICIENT_OBS",
            )
            continue

        try:
            adf_result = adfuller(
                y.to_numpy(),
                maxlag=maxlag,
                regression=adf_regression,
                autolag=autolag,
            )
        except Exception:
            last_result = DStarResult(
                feature=feature,
                d_star=None,
                tested_d=d,
                adf_stat=None,
                adf_pvalue=None,
                adf_rejects=False,
                n_raw=len(x),
                n_ffd=len(y),
                width=width,
                corr=corr,
                status="ADF_FAILED",
            )
            continue

        adf_stat = float(adf_result[0])
        adf_pvalue = float(adf_result[1])
        rejects = bool(adf_pvalue <= adf_alpha)

        result = DStarResult(
            feature=feature,
            d_star=d if rejects else None,
            tested_d=d,
            adf_stat=adf_stat,
            adf_pvalue=adf_pvalue,
            adf_rejects=rejects,
            n_raw=len(x),
            n_ffd=len(y),
            width=width,
            corr=corr,
            status="STATIONARY" if rejects else "NON_STATIONARY",
        )

        if rejects:
            return result

        last_result = result

    if last_result is None:
        raise RuntimeError("d* estimation failed unexpectedly.")

    return DStarResult(
        feature=last_result.feature,
        d_star=None,
        tested_d=last_result.tested_d,
        adf_stat=last_result.adf_stat,
        adf_pvalue=last_result.adf_pvalue,
        adf_rejects=False,
        n_raw=last_result.n_raw,
        n_ffd=last_result.n_ffd,
        width=last_result.width,
        corr=last_result.corr,
        status="NO_ADMISSIBLE_D",
    )


def estimate_d_star_frame(
    data: pd.DataFrame,
    d_grid: Iterable[float],
    threshold: float,
    adf_alpha: float,
    min_obs: int,
    *,
    adf_regression: str = "c",
    autolag: str | None = None,
    maxlag: int | None = 1,
    fill_method: str | None = None,
) -> pd.DataFrame:
    """Apply estimate_d_star to every column of a DataFrame.

    Defaults match estimate_d_star: ADF parameters follow López de Prado
    (2018, snippet 5.4) and no forward fill is applied by default.
    """
    records = []

    for column in data.columns:
        result = estimate_d_star(
            series=data[column],
            d_grid=d_grid,
            threshold=threshold,
            adf_alpha=adf_alpha,
            min_obs=min_obs,
            feature=str(column),
            adf_regression=adf_regression,
            autolag=autolag,
            maxlag=maxlag,
            fill_method=fill_method,
        )
        records.append(result.to_dict())

    return pd.DataFrame.from_records(records)
