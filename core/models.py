import string
from bisect import (
    bisect_left,
)
from functools import (
    lru_cache,
    partial,
)
from itertools import (
    dropwhile,
    repeat,
)
from operator import (
    eq,
)
from typing import (
    Callable,
    Dict,
    List,
)

from django.conf import (
    settings,
)
from django.db import (
    models,
)
from django.db.models.base import (
    ModelBase,
)


class HierarchicalMeta(ModelBase):
    ALLOWED_CHARACTERS = ''.join((
        string.digits,
        string.ascii_uppercase,
        string.ascii_lowercase,
    ))
    DELIMITER = '-'

    @classmethod
    @lru_cache(maxsize=None)
    def get_ids_by_char_cache(mcs) -> Dict[str, int]:
        return dict(map(
            reversed,
            enumerate(mcs.ALLOWED_CHARACTERS),
        ))

    @classmethod
    def get_char_idx(mcs, char: str) -> int:
        if settings.DEBUG:
            try:
                return mcs.get_ids_by_char_cache()[char]
            except KeyError:
                raise ValueError(
                    f'Character "{char}" is not allowed!',
                )

        return bisect_left(mcs.ALLOWED_CHARACTERS, char)

    @classmethod
    @lru_cache(maxsize=None)
    def get_zero_predicate(mcs) -> Callable[[str], bool]:
        return partial(eq, mcs.ALLOWED_CHARACTERS[0])

    @classmethod
    def _make_next_id(mcs, chars: str):
        max_char: str = mcs.ALLOWED_CHARACTERS[-1]
        min_char: str = mcs.ALLOWED_CHARACTERS[0]

        result_list_len = len(chars) + 1
        result_list: List[str] = [min_char] * result_list_len
        result_list[1:] = chars

        reversed_enumerated_chars = zip(
            range(len(chars), 0, -1),
            reversed(chars),
        )
        first_idx = 1
        for idx, char in reversed_enumerated_chars:
            if char != max_char:
                next_char = mcs.ALLOWED_CHARACTERS[1 + mcs.get_char_idx(char)]
                result_list[idx] = next_char
                first_idx = idx+1
                break
        else:
            result_list[0] = mcs.ALLOWED_CHARACTERS[1]

        result_list[first_idx:result_list_len] = repeat(
            min_char,
            result_list_len-first_idx,
        )

        return ''.join(dropwhile(
            mcs.get_zero_predicate(),
            result_list,
        ))

    def get_max_str_id(cls) -> str:
        full_id: str = next(
            iter(cls.objects.aggregate(
                models.Max('id'),
            ).values()),
            None,
        )
        if full_id is None:
            return cls.ALLOWED_CHARACTERS[0]

        return full_id.split(
            sep=cls.DELIMITER,
            maxsplit=1,
        )[0]


class Hierarchical(models.Model, metaclass=HierarchicalMeta):
    id = models.TextField(
        primary_key=True,
    )

    parent = models.ForeignKey(
        to='self',
        on_delete=models.PROTECT,
        related_name='children',
        null=True,
        verbose_name='Обобщение',
    )

    class Meta:
        abstract = True

    @classmethod
    def get_next_id(cls) -> str:
        chars: str = cls.get_max_str_id()
        return cls._make_next_id(chars)

    def save(
            self,
            force_insert=False,
            force_update=False,
            using=None,
            update_fields=None,
    ):
        own_id_chunk = self.get_next_id()
        if self.parent is None:
            self.id = own_id_chunk
        else:
            self.id = self.__class__.DELIMITER.join((
                own_id_chunk,
                self.parent.id,
            ))
        super().save(force_insert, force_update, using, update_fields)
