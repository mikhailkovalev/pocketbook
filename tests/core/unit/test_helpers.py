import pytest

from core import helpers


@pytest.mark.parametrize(
    [
        'tracker_kwargs',
        'expected_result_type',
    ],
    [
        [
            {},  # tracker_kwargs
            float,  # expected_result_type
        ],
        [
            {'use_ns': False},  # tracker_kwargs
            float,  # expected_result_type
        ],
        [
            {'use_ns': True},  # tracker_kwargs
            int,  # expected_result_type
        ],
    ],
)
def test_track_time(
        tracker_kwargs: dict,
        expected_result_type: type,
):
    with helpers.track_time(**tracker_kwargs) as tracker:
        pass

    assert isinstance(tracker.elapsed_time, expected_result_type)
