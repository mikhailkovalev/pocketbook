from itertools import (
    chain,
)
from typing import Iterable, Tuple


class BaseEnumerate:
    """
    Базовый класс перечислений.

    Предоставляет более удобный интерфейс для
    взаимодействия с джанговскими моделями и
    формами.
    """
    values = {}

    empty_label: str = '---------'

    @classmethod
    def get_choices(cls, with_empty: bool = False):
        """
        Используется для ограничения полей ORM и
        в качестве источника данных в ChoiceField
        """
        pairs: Iterable[Tuple] = cls.values.items()
        if with_empty:
            pairs = chain(
                (
                    (None, cls.empty_label),
                ),
                pairs,
            )
        return tuple(pairs)
