from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Iterable

import pandas as pd


@dataclass(frozen=True)
class Segment:
    segment_id: str
    start: pd.Timestamp
    end: pd.Timestamp
    n_obs: int

    def to_dict(self) -> dict:
        return asdict(self)


def build_segments_from_boundaries(
    index: pd.DatetimeIndex,
    boundaries: Iterable[pd.Timestamp | str],
    *,
    min_obs: int = 1,
    segment_prefix: str = "segment",
) -> pd.DataFrame:
    if not isinstance(index, pd.DatetimeIndex):
        raise TypeError("index must be a pandas DatetimeIndex.")
    if not index.is_monotonic_increasing:
        raise ValueError("index must be ordered ascending.")
    if not index.is_unique:
        raise ValueError("index must contain unique timestamps.")
    if min_obs <= 0:
        raise ValueError("min_obs must be positive.")

    boundary_positions = sorted(index.get_loc(pd.Timestamp(b)) for b in boundaries)

    if any(pos == 0 for pos in boundary_positions):
        raise ValueError("Boundary cannot be the first index value.")

    cuts = [0, *boundary_positions, len(index)]
    segments: list[Segment] = []

    for i in range(len(cuts) - 1):
        start_pos = cuts[i]
        end_pos = cuts[i + 1]

        segment_index = index[start_pos:end_pos]
        n_obs = len(segment_index)

        if n_obs < min_obs:
            raise ValueError(
                f"Segment {i + 1} has {n_obs} observations; "
                f"minimum required is {min_obs}."
            )

        segments.append(
            Segment(
                segment_id=f"{segment_prefix}_{i + 1}",
                start=segment_index[0],
                end=segment_index[-1],
                n_obs=n_obs,
            )
        )

    return pd.DataFrame.from_records([s.to_dict() for s in segments])


def validate_segments(
    segments: pd.DataFrame,
    *,
    start_col: str = "start",
    end_col: str = "end",
    min_obs_col: str = "n_obs",
    min_obs: int = 1,
) -> None:
    required = {start_col, end_col, min_obs_col}
    missing = required.difference(segments.columns)

    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    ordered = segments.sort_values(start_col).reset_index(drop=True)

    if (ordered[min_obs_col] < min_obs).any():
        raise ValueError("At least one segment violates min_obs.")

    for i in range(1, len(ordered)):
        prev_end = pd.Timestamp(ordered.loc[i - 1, end_col])
        curr_start = pd.Timestamp(ordered.loc[i, start_col])

        if curr_start <= prev_end:
            raise ValueError("Segments overlap or are not strictly ordered.")
