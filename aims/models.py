from decimal import (
    Decimal,
)
from typing import (
    Optional,
)

from django.db import (
    models,
)
from mptt.fields import (
    TreeForeignKey,
)

from core.helpers import (
    AbleToVerbolizeDateTimeAttrsMixin,
)
from core.hierarchical.models import (
    Hierarchical,
)


class Aim(Hierarchical, AbleToVerbolizeDateTimeAttrsMixin):
    name = models.CharField(
        max_length=50,
        verbose_name='Наименование',
    )
    created = models.DateField(
        verbose_name='Момент создания записи',
    )

    start_day = models.DateField(
        verbose_name='Дата начала',
        null=True,
    )

    deadline = models.DateField(
        verbose_name='Дата завершения',
        null=True,
    )
    estimated_time = models.IntegerField(
        verbose_name='Оценка времени (часов)',
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = 'Цель'
        verbose_name_plural = 'Цели'

    @property
    def elapsed_time(self) -> Decimal:
        subtree_ids = self.get_descendants(
            include_self=True,
        ).values_list(
            'pk',
            flat=True,
        )

        return sum(self.actions.model.objects.filter(
            aim__in=subtree_ids,
        ).values_list(
            'elapsed_time',
            flat=True,
        )) or None

    def __str__(self) -> str:
        self.name: str
        return self.name

    def verbose_start_day(self) -> Optional[str]:
        return self.get_verbose_date(
            attr='start_day',
        )
    verbose_start_day.short_description = 'start day'

    def verbose_deadline(self) -> Optional[str]:
        return self.get_verbose_date(
            attr='deadline',
        )
    verbose_deadline.short_description = 'deadline'

    def verbose_created(self) -> Optional[str]:
        return self.get_verbose_date(
            attr='created',
        )
    verbose_created.short_description = 'created'

    @classmethod
    def get_own_ids(cls, owner_id):
        hierarchy_model = cls.aimhierarchy.related.related_model
        root_ids = hierarchy_model.objects.filter(
            whose_id=owner_id,
        ).values_list(
            'root_id',
            flat=True,
        )
        return cls.objects.filter(
            pk__in=root_ids,
        ).get_descendants(
            include_self=True,
        ).values_list(
            'pk',
            flat=True,
        )


AimHierarchyBase = Aim.get_hierarchy_cls()


class AimHierarchy(AimHierarchyBase):
    pass


class Action(models.Model, AbleToVerbolizeDateTimeAttrsMixin):
    aim = TreeForeignKey(
        to=Aim,
        on_delete=models.CASCADE,
        related_name='actions',
        verbose_name='Цель',
    )

    when = models.DateField(
        verbose_name='Дата действия',
    )
    description = models.CharField(
        max_length=800,
        blank=True,
        null=True,
        verbose_name='Описание',
    )
    elapsed_time = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        verbose_name='Затрачено времени (часов)',
    )

    class Meta:
        verbose_name = 'Действие'
        verbose_name_plural = 'Действия'

    def short_description(self, max_length=20, ending='<...>'):
        self.description: Optional[str]
        result: str = self.description or ''
        if len(result) > max_length:
            result = ''.join((
                result[:max_length - len(ending)],
                ending,
            ))
        return result

    def verbose_when(self):
        return self.get_verbose_date(
            attr='when',
        )
    verbose_when.short_description = 'when'

    def __str__(self):
        return ': '.join((
            self.verbose_when(),
            self.short_description(),
        ))
