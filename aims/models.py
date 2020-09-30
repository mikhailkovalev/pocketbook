from decimal import (
    Decimal,
)

from django.db import (
    models,
)

from core.hierarchical.models import (
    Hierarchical,
)


class Aim(Hierarchical):
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
    finish_day = models.DateField(
        verbose_name='Дата завершения',
        null=True,
    )
    estimated_time = models.IntegerField(
        verbose_name='Оценка времени (часов)',
        null=True,
    )

    class Meta:
        verbose_name = 'Цель'
        verbose_name_plural = 'Цели'

    @property
    def elapsed_time(self) -> Decimal:
        return Decimal()


AimHierarchyBase = Aim.get_hierarchy_cls()


class AimHierarchy(AimHierarchyBase):
    pass


class Action(models.Model):
    aim = models.ForeignKey(
        to=Aim,
        on_delete=models.CASCADE,
        related_name='steps',
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
