import pandas as pd
import pytest

from segmentation.boundaries import (
    build_segments_from_boundaries,
    validate_segments,
)


def test_build_segments_from_single_boundary_is_non_overlapping():
    index = pd.date_range("2020-01-01", periods=10, freq="D")

    segments = build_segments_from_boundaries(
        index,
        boundaries=["2020-01-05"],
    )

    assert len(segments) == 2
    assert segments.loc[0, "start"] == pd.Timestamp("2020-01-01")
    assert segments.loc[0, "end"] == pd.Timestamp("2020-01-04")
    assert segments.loc[0, "n_obs"] == 4

    assert segments.loc[1, "start"] == pd.Timestamp("2020-01-05")
    assert segments.loc[1, "end"] == pd.Timestamp("2020-01-10")
    assert segments.loc[1, "n_obs"] == 6

    validate_segments(segments)


def test_build_segments_from_multiple_boundaries():
    index = pd.date_range("2020-01-01", periods=10, freq="D")

    segments = build_segments_from_boundaries(
        index,
        boundaries=["2020-01-04", "2020-01-08"],
    )

    assert segments["n_obs"].tolist() == [3, 4, 3]
    assert segments["segment_id"].tolist() == [
        "segment_1",
        "segment_2",
        "segment_3",
    ]

    validate_segments(segments)


def test_boundary_cannot_be_first_observation():
    index = pd.date_range("2020-01-01", periods=10, freq="D")

    with pytest.raises(ValueError, match="Boundary cannot be the first index value"):
        build_segments_from_boundaries(
            index,
            boundaries=["2020-01-01"],
        )


def test_boundary_must_exist_in_index():
    index = pd.date_range("2020-01-01", periods=10, freq="D")

    with pytest.raises(KeyError):
        build_segments_from_boundaries(
            index,
            boundaries=["2020-02-01"],
        )


def test_validate_segments_rejects_overlap():
    segments = pd.DataFrame(
        {
            "start": [pd.Timestamp("2020-01-01"), pd.Timestamp("2020-01-03")],
            "end": [pd.Timestamp("2020-01-05"), pd.Timestamp("2020-01-10")],
            "n_obs": [5, 8],
        }
    )

    with pytest.raises(ValueError, match="Segments overlap"):
        validate_segments(segments)
