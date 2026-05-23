from __future__ import annotations

import numpy as np
import pandas as pd


def get_ffd_weights(d: float, threshold: float) -> np.ndarray:
    if d < 0:
        raise ValueError("d must be non-negative.")
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


def fracdiff_ffd(
    series: pd.Series,
    d: float,
    threshold: float,
    *,
    fill_method: str | None = "ffill",
) -> pd.Series:
    x = series.astype(float).replace([np.inf, -np.inf], np.nan)

    if fill_method == "ffill":
        x = x.ffill()
    elif fill_method is not None:
        x = x.fillna(method=fill_method)

    x = x.dropna()

    if x.empty:
        return pd.Series(dtype=float, name=series.name)

    weights = get_ffd_weights(d=d, threshold=threshold)
    width = len(weights)

    if len(x) < width:
        return pd.Series(dtype=float, name=series.name)

    values = x.to_numpy()
    output = [
        float(np.dot(weights, values[i - width + 1 : i + 1]))
        for i in range(width - 1, len(values))
    ]

    return pd.Series(
        output,
        index=x.index[width - 1 :],
        name=series.name,
    )


def get_ffd_width(d: float, threshold: float) -> int:
    return len(get_ffd_weights(d=d, threshold=threshold))
