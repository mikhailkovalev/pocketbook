from functools import (
    lru_cache,
)
from typing import (
    Type,
)

from django.db import (
    models,
)

from mptt.models import (
    MPTTModel,
    TreeForeignKey,
)

from .managers import (
    HierarchicalManager,
)


class Hierarchical(MPTTModel):
    objects = HierarchicalManager()

    parent = TreeForeignKey(
        to='self',
        on_delete=models.PROTECT,
        related_name='children',
        null=True,
        blank=True,
        verbose_name='Обобщение',
    )

    class Meta:
        abstract = True

    @classmethod
    @lru_cache(maxsize=None)
    def get_hierarchy_cls(cls, ownable: bool = True) -> Type[models.Model]:
        attrs = {
            # Fields
            'root': models.OneToOneField(
                to=cls,
                on_delete=models.CASCADE,
                verbose_name='Корневой элемент иерархии',
            ),

            # Meta
            '__module__': cls.__module__,
            'Meta': type('Meta', (), dict(abstract=True)),
        }

        if ownable:
            attrs['whose'] = models.ForeignKey(
                to='auth.User',
                on_delete=models.CASCADE,
                related_name='+',
                verbose_name='Владелец иерархии',
            )

        return type(  # noqa
            f'{cls.__name__}HierarchyBase',
            (models.Model,),
            attrs,
        )
