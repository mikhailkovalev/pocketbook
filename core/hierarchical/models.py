from functools import (
    lru_cache,
)
from typing import (
    Any,
    Dict,
    Type,
)

from django.db import (
    models,
)
from mptt.models import (
    MPTTModel,
    MPTTModelBase,
    TreeForeignKey,
)

from .helpers import (
    get_own_items_ids,
)
from .managers import (
    HierarchicalManager,
)


class HierarchicalOptions:

    ownable: bool = True
    root_attr: str = 'root'
    owner_attr: str = 'whose'

    def __init__(self, options: Dict[str, Any]):
        options_items = (
            (attr, value)
            for attr, value in options.items()
            if not attr.startswith('__')
        )
        for attr, value in options_items:
            setattr(self, attr, value)

    def items(self):
        return (
            (k, v)
            for k, v in self.__dict__.items()
            if not k.startswith('_')
        )


class HierarchicalBase(MPTTModelBase):
    def __new__(mcs, name, bases, attrs):
        HierarchicalMeta = attrs.pop('HierarchicalMeta', None)

        if HierarchicalMeta is None:
            class HierarchicalMeta:
                pass

        options: Dict[str, Any] = {}
        for base in reversed(bases):
            base_meta = getattr(base, '_hierarchical_meta', None)
            if base_meta is None:
                continue
            options.update(base_meta.items())

        options.update(HierarchicalMeta.__dict__)
        
        attrs['_hierarchical_meta'] = HierarchicalOptions(
            options=options,
        )
        return super().__new__(mcs, name, bases, attrs)


class Hierarchical(MPTTModel, metaclass=HierarchicalBase):
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
    def get_hierarchy_cls(cls) -> Type[models.Model]:
        attrs = {
            # Fields
            cls._hierarchical_meta.root_attr: models.OneToOneField(
                to=cls,
                on_delete=models.CASCADE,
                verbose_name='Корневой элемент иерархии',
            ),

            # Meta
            '__module__': cls.__module__,
            '_hierarchical_meta': cls._hierarchical_meta,
            'Meta': type('Meta', (), dict(abstract=True)),
        }

        if cls._hierarchical_meta.ownable:
            attrs[cls._hierarchical_meta.owner_attr] = models.ForeignKey(
                to='auth.User',
                on_delete=models.CASCADE,
                related_name='+',
                verbose_name='Владелец иерархии',
            )
            attrs['get_own_items_ids'] = classmethod(
                get_own_items_ids,
            )

        return type(  # noqa
            f'{cls.__name__}HierarchyBase',
            (models.Model,),
            attrs,
        )
