from typing import Any, Dict

import dirty_equals
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User


class _NO_ONE:
    def __eq__(self, other):
        return False

    def __ne__(self, other):
        return True

    def __repr__(self):
        return '<NO_ONE>'


NO_ONE = _NO_ONE


class CheckPassword(dirty_equals.DirtyEquals):
    def __init__(self, raw_password):
        super().__init__()
        self._raw_password = raw_password

    def equals(self, encoded_password: str) -> bool:
        return check_password(self._raw_password, encoded_password)


class CheckWhose(dirty_equals.DirtyEquals):
    def __init__(self, username: str):
        super().__init__()
        self._username = username

    @staticmethod
    def _get_user_id_by_name(username) -> int:
        try:
            return User.objects.filter(
                username=username,
            ).values_list(
                'id',
                flat=True,
            ).get()
        except User.DoesNotExist:
            return NO_ONE

    def equals(self, user_id: int) -> bool:
        return user_id == self._get_user_id_by_name(self._username)

    def __repr__(self):
        return f'{self.__class__.__name__}({self._username!r})'


# todo: remove?
def compare_dicts(lhs: Dict[str, Any], rhs: Dict[str, Any]) -> None:
    pass