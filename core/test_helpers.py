import dirty_equals
from django.contrib.auth.hashers import check_password


class CheckPassword(dirty_equals.DirtyEquals):
    def __init__(self, raw_password):
        super().__init__()
        self._raw_password = raw_password

    def equals(self, encoded_password: str) -> bool:
        return check_password(self._raw_password, encoded_password)
