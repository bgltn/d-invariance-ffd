from __future__ import annotations

import numpy as np
import pandas as pd


def get_ffd_weights(d: float, threshold: float = 1e-5) -> np.ndarray:
    """
    Return fixed-width fractional-differencing weights.

    The returned vector is ordered from oldest to newest observation, so it can
    be directly dotted with a chronological rolling window.

    Examples:
    - d = 0 -> [1.0]
    - d = 1 -> [-1.0, 1.0]
    """
    if not (0.0 <= d <= 1.0):
        raise ValueError("d must be in [0, 1].")

    if threshold <= 0:
        raise ValueError("threshold must be strictly positive.")

    weights = [1.0]
    k = 1

    while True:
        weight = -weights[-1] * (d - k + 1) / k

        if abs(weight) < threshold:
            break

        weights.append(weight)
        k += 1

    return np.asarray(weights[::-1], dtype=float)


def get_ffd_width(d: float, threshold: float = 1e-5) -> int:
    """
    Return the retained fixed-width window length.
    """
    return int(len(get_ffd_weights(d=d, threshold=threshold)))


def fracdiff_ffd(
    series: pd.Series,
    d: float,
    threshold: float = 1e-5,
    fill_method: str | None = None,
) -> pd.Series:
    """
    Apply Fixed-width Fractional Differencing to one indexed series.

    Missing-data policy:
    - fill_method=None: do not impute; skip windows containing missing values.
    - fill_method="ffill": explicitly forward-fill before transformation.

    Forward fill is not the default because carry-forward imputation can alter
    persistence and therefore affect the selected order d*.
    """
    if fill_method not in (None, "ffill"):
        raise ValueError("fill_method must be None or 'ffill'.")

    x = pd.Series(series, copy=True).astype(float)

    if fill_method == "ffill":
        x = x.ffill()

    weights = get_ffd_weights(d=d, threshold=threshold)
    width = len(weights)

    if x.dropna().empty or len(x) < width:
        return pd.Series(dtype=float, name=getattr(series, "name", None))

    values = x.to_numpy(dtype=float)
    index = x.index

    out: list[float] = []
    out_index = []

    for iloc in range(width - 1, len(values)):
        window = values[iloc - width + 1 : iloc + 1]

        if not np.isfinite(window).all():
            continue

        out.append(float(np.dot(weights, window)))
        out_index.append(index[iloc])

    return pd.Series(out, index=out_index, name=getattr(series, "name", None))


# Compatibility aliases for notebooks / older examples.
get_weights_ffd = get_ffd_weights


def fracdiff_ffd_series(
    series: pd.Series,
    d: float,
    tau: float = 1e-5,
    fill_method: str | None = None,
) -> tuple[pd.Series, int]:
    """
    Notebook-compatible wrapper returning both transformed series and width.
    """
    transformed = fracdiff_ffd(
        series=series,
        d=d,
        threshold=tau,
        fill_method=fill_method,
    )
    width = get_ffd_width(d=d, threshold=tau)
    return transformed, width
