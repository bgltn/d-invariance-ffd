import numpy as np
import pandas as pd

from ffd import estimate_d_star, compute_d_invariance_statistic
from segmentation import build_segments_from_boundaries


def make_synthetic_series(n: int = 300, seed: int = 7) -> pd.Series:
    rng = np.random.default_rng(seed)
    innovations = rng.standard_normal(n)
    values = np.cumsum(innovations)

    index = pd.date_range("2020-01-01", periods=n, freq="B")

    return pd.Series(values, index=index, name="synthetic_feature")


def main() -> None:
    series = make_synthetic_series()

    segments = build_segments_from_boundaries(
        series.index,
        boundaries=["2020-05-20", "2020-10-07"],
        min_obs=30,
    )

    records = []

    for _, segment in segments.iterrows():
        window = series.loc[segment["start"] : segment["end"]]

        result = estimate_d_star(
            series=window,
            d_grid=[0.0, 0.5, 1.0],
            threshold=1e-3,
            adf_alpha=0.05,
            min_obs=30,
            feature=series.name,
        )

        records.append(
            {
                "feature_id": series.name,
                "window_id": segment["segment_id"],
                "window_order": int(segment["segment_id"].split("_")[-1]),
                "d_star": result.d_star,
            }
        )

    registry = pd.DataFrame.from_records(records).dropna(subset=["d_star"])
    statistic = compute_d_invariance_statistic(registry)

    print("Segments")
    print(segments)
    print("\nSynthetic d* registry")
    print(registry)
    print("\nd-invariance statistic")
    print(statistic)


if __name__ == "__main__":
    main()
