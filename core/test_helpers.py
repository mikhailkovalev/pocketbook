from typing import Sequence, Type

import dirty_equals
from django.conf import settings
from django.contrib.auth.hashers import check_password
from django.db.models import Model


class CheckPassword(dirty_equals.DirtyEquals):
    def __init__(self, raw_password):
        super().__init__()
        self._raw_password = raw_password

    def equals(self, encoded_password: str) -> bool:
        return check_password(self._raw_password, encoded_password)


class IsNow(dirty_equals.IsNow):
    def __init__(self, **kwargs):
        kwargs.setdefault('tz', settings.TIME_ZONE)
        kwargs.setdefault('enforce_tz', False)
        super().__init__(**kwargs)


def test_db_objs(
    model: Type[Model],
    ordering: Sequence[str],
):
    def __test_db_objs(db_data, db_data_filename, expected_objs_data, model_to_dict):
        actual_objs = model.objects.order_by(*ordering)
        assert len(actual_objs) == len(expected_objs_data)
        for idx, (actual_obj, expected_obj_data) in enumerate(
            zip(actual_objs, expected_objs_data),
        ):
            actual_obj_data = model_to_dict(actual_obj)
            assert sorted(actual_obj_data) == sorted(expected_obj_data)
            for field_name, actual_value in actual_obj_data.items():
                assert actual_value == expected_obj_data[field_name], \
                    f'idx={idx!r}; field_name={field_name!r}'

    return __test_db_objs
