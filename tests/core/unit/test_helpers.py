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


@pytest.mark.parametrize(
    ['arg', 'expected_value'],
    [
        [[], []],
        [[1], []],
        [[1, 2], [(1, 2)]],
        [[1, 2, 3], [(1, 2), (2, 3)]],
        [[1, 2, 3, 4], [(1, 2), (2, 3), (3, 4)]],
        [range(3), [(0, 1), (1, 2)]],
        [iter(range(3)), [(0, 1), (1, 2)]],
    ],
)
def test_iter_pairs(arg, expected_value):
    assert list(helpers.iter_pairs(arg)) == expected_value


@pytest.mark.parametrize(
    ['kwargs', 'expected_value'],
    [
        # region: empty sequence
        [{'iterable': []}, True],
        [{'iterable': [], 'reversed': True}, True],
        [{'iterable': [], 'reversed': False}, True],
        [{'iterable': [], 'key': lambda x: -x, 'reversed': True}, True],
        [{'iterable': [], 'key': lambda x: -x, 'reversed': False}, True],
        # endregion
        # region single item sequence
        [{'iterable': [1]}, True],
        [{'iterable': [1], 'reversed': True}, True],
        [{'iterable': [1], 'reversed': False}, True],
        [{'iterable': [1], 'key': lambda x: -x, 'reversed': True}, True],
        [{'iterable': [1], 'key': lambda x: -x, 'reversed': False}, True],
        # endregion
        # region pair items
        [{'iterable': [1, 1]}, True],
        [{'iterable': [1, 1], 'reversed': True}, True],
        [{'iterable': [1, 1], 'reversed': False}, True],
        [{'iterable': [1, 1], 'key': lambda x: -x, 'reversed': True}, True],
        [{'iterable': [1, 1], 'key': lambda x: -x, 'reversed': False}, True],

        [{'iterable': [1, 2]}, True],
        [{'iterable': [1, 2], 'reversed': True}, False],
        [{'iterable': [1, 2], 'reversed': False}, True],
        [{'iterable': [1, 2], 'key': lambda x: -x, 'reversed': True}, True],
        [{'iterable': [1, 2], 'key': lambda x: -x, 'reversed': False}, False],

        [{'iterable': [2, 1]}, False],
        [{'iterable': [2, 1], 'reversed': True}, True],
        [{'iterable': [2, 1], 'reversed': False}, False],
        [{'iterable': [2, 1], 'key': lambda x: -x, 'reversed': True}, False],
        [{'iterable': [2, 1], 'key': lambda x: -x, 'reversed': False}, True],
        # endregion
        # region triple items
        [{'iterable': [1, 1, 1]}, True],
        [{'iterable': [1, 1, 1], 'reversed': True}, True],
        [{'iterable': [1, 1, 1], 'reversed': False}, True],
        [{'iterable': [1, 1, 1], 'key': lambda x: -x, 'reversed': True}, True],
        [{'iterable': [1, 1, 1], 'key': lambda x: -x, 'reversed': False}, True],

        [{'iterable': [1, 2, 3]}, True],
        [{'iterable': [1, 2, 3], 'reversed': True}, False],
        [{'iterable': [1, 2, 3], 'reversed': False}, True],
        [{'iterable': [1, 2, 3], 'key': lambda x: -x, 'reversed': True}, True],
        [{'iterable': [1, 2, 3], 'key': lambda x: -x, 'reversed': False}, False],

        [{'iterable': [2, 1, 3]}, False],
        [{'iterable': [2, 1, 3], 'reversed': True}, False],
        [{'iterable': [2, 1, 3], 'reversed': False}, False],
        [{'iterable': [2, 1, 3], 'key': lambda x: 12 + x*(-11 + x*3), 'reversed': True}, False],
        [{'iterable': [2, 1, 3], 'key': lambda x: 12 + x*(-11 + x*3), 'reversed': False}, True],
        # endregion
    ],
)
def test_is_sorted(kwargs, expected_value):
    assert helpers.is_sorted(**kwargs) == expected_value


@pytest.mark.parametrize(
    ['kwargs', 'expected_result'],
    [
        [
            {
                'dest_args': [-0.2, 0., 0.2, 0.4, 0.6, 0.8, 1., 1.1],
                'source_args': [0, 1],
                'source_values': [0, 1],
            },
            [-0.2, 0., 0.2, 0.4, 0.6, 0.8, 1., 1.1],
        ],
        [
            {
                'dest_args': [1.1, 0.6, -0.2, 0.2, 0.0, 0.4, 0.8, 1.0],
                'source_args': [0, 1],
                'source_values': [0, 1],
            },
            [1.1, 0.6, -0.2, 0.2, 0.0, 0.4, 0.8, 1.0],
        ],
        [
            {
                'dest_args': [-0.4, 0.0, 0.4, 0.8, 1.2, 1.6, 2.0, 2.2],
                'source_args': [0, 1, 2],
                'source_values': [0, 1, 2],
            },
            [-0.4, 0.0, 0.4, 0.8, 1.2, 1.6, 2.0, 2.2],
        ],
        [
            {
                'dest_args': [-0.4, 0.0, 0.4, 0.8, 1.2, 1.6, 2.0, 2.2],
                'source_args': [1, 0, 2],
                'source_values': [1, 0, 2],
            },
            [-0.4, 0.0, 0.4, 0.8, 1.2, 1.6, 2.0, 2.2],
        ],
        [
            {
                'dest_args': [
                    0.1,
                    0.15,
                    0.19,
                    0.20,
                    0.21,
                    0.25,
                    0.29,
                    0.3,
                    0.31,
                    0.36,
                    0.39,
                    0.4,
                    0.41,
                    0.44,
                    0.47,
                    0.49,
                    0.5,
                    0.51,
                    0.52,
                    0.58,
                    0.59,
                    0.6,
                    0.61,
                    0.65,
                    0.69,
                    0.7,
                    0.77,
                    0.79,
                    0.8,
                    0.81,
                    0.89,
                    0.9,
                ],
                'source_args': [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9],
                'source_values': [10, 5, 3.33, 2.5, 2, 1.67, 1.43, 1.25, 1.11],
            },
            [
                10,
                7.5,
                5.5,
                5.0,
                4.833,
                4.165,
                3.497,
                3.33,
                3.247,
                2.832,
                2.583,
                2.5,
                2.45,
                2.3,
                2.15,
                2.05,
                2.0,
                1.967,
                1.934,
                1.736,
                1.703,
                1.67,
                1.646,
                1.55,
                1.454,
                1.43,
                1.304,
                1.268,
                1.25,
                1.236,
                1.124,
                1.11,
            ],
        ],
    ],
)
def test_numpy_interp(kwargs, expected_result):
    actual_result = helpers.numpy_interp(**kwargs)
    assert len(actual_result) == len(expected_result)
    for idx, (actual_item, expected_item) in enumerate(zip(actual_result, expected_result)):
        assert abs(actual_item - expected_item) < 1e-8, f'idx={idx}: actual={actual_item}, expected={expected_item}'