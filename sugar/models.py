from collections import defaultdict
from datetime import datetime
from decimal import Decimal
from typing import (
    Optional,
)

from django.db import (
    models,
)

from core.helpers import (
    AbleToVerbolizeDateTimeAttrsMixin,
    NumericSum,
    with_server_timezone,
)


class Record(models.Model):
    """
    Содержит информацию о
    пользователе, создавшем запись, а также о
    моменте создания.
    """
    who = models.ForeignKey(
        to='auth.User',
        on_delete=models.CASCADE,
        related_name='records',
        verbose_name='Автор',
    )
    when = models.DateTimeField(
        verbose_name='Момент создания записи',
    )

    def when_verbose(self):
        assert isinstance(
            self.when, datetime)
        return with_server_timezone(
            self.when
        ).strftime(
            '%Y-%m-%d %H:%M')

    def sugar_level(self):
        sugar_meterings = SugarMetering.objects.filter(
            record=self.pk)
        assert sugar_meterings.count() <= 1
        return sugar_meterings.values_list(
            'sugar_level',
            flat=True
        ).first()

    def meal_info(self) -> Optional[str]:
        meals = Meal.objects.filter(
            record=self.pk
        )
        if not meals.exists():
            return

        return '+'.join(map(str, meals.values_list(
            'food_quantity',
            flat=True,
        )))

    def total_meal(self) -> Optional[Decimal]:
        meals = Meal.objects.filter(
            record=self.pk
        )
        if not meals.exists():
            return

        return sum(meals.values_list(
            'food_quantity',
            flat=1,
        ))

    def injections_info(self):
        injections = InsulinInjection.objects.filter(
            record=self.pk
        )
        if injections.count() == 0:
            return

        injections_by_kind = defaultdict(list)
        injections = injections.values_list(
            'insulin_syringe__insulin_mark__name',
            'insulin_quantity',
        )
        for kind, quantity in injections:
            injections_by_kind[kind].append(quantity)

        return ', '.join(
            '{} {}'.format(
                '+'.join(map(str, quantities)),
                kind
            )
            for kind, quantities
            in injections_by_kind.items()
        )

    def short_comments(self):
        comments = tuple(
            comment.short()
            for comment in Comment.objects.filter(
                record=self.pk)
        )
        if not comments:
            return

        return '; '.join(comments)

    class Meta:
        verbose_name = 'Запись дневника сахаров'
        verbose_name_plural = 'Записи дневника сахаров'

        ordering = (
            'who',
            '-when',
        )


class Attachment(models.Model):
    """
    Прикрепление к записи. На каждую запись может
    ссылаться неограничено много прикреплений
    различных типов.
    """
    record = models.ForeignKey(
        to=Record,
        on_delete=models.CASCADE,
        verbose_name='Запись',
    )

    class Meta:
        abstract = True
        verbose_name = 'Прикрепление к записи'
        verbose_name_plural = 'Прикрепления к записям'


class Meal(Attachment):
    """
    Приём пищи
    """
    food_quantity = models.DecimalField(
        verbose_name='Количество употреблённых углеводов (ХЕ)',
        max_digits=3,
        decimal_places=1,
    )
    description = models.CharField(
        verbose_name='Описание',
        max_length=50,
        blank=True,
        default='',
    )

    def __str__(self):
        prefix = (
            self.description
            or self._meta.verbose_name
        )
        return '{}: {}ХЕ'.format(
            prefix,
            self.food_quantity,
        )

    class Meta:
        verbose_name = 'Приём пищи'
        verbose_name_plural = 'Приёмы пищи'


class InsulinKind(models.Model):
    """
    Вид инсулина
    """
    name = models.CharField(
        verbose_name='Наименование',
        max_length=50,
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Вид инсулина'
        verbose_name_plural = 'Виды инсулина'


class InsulinInjection(Attachment):
    """
    Инъекция инсулина
    """
    insulin_syringe = models.ForeignKey(
        to='InsulinSyringe',
        on_delete=models.PROTECT,
        verbose_name='Шприц',
        related_name='injections',
    )
    insulin_quantity = models.PositiveSmallIntegerField(
        verbose_name='Количество введённого инсулина',
        null=True,
    )

    def get_insulin_mark(self):
        return self.insulin_syringe.insulin_mark

    def __str__(self):
        return 'Инъекция({}): {}ед.'.format(
            self.get_insulin_mark().name,
            self.insulin_quantity,
        )

    class Meta:
        verbose_name = 'Инъекция инсулина'
        verbose_name_plural = 'Инъекции инсулина'


class SugarMetering(Attachment):
    """
    Уровень сахара в крови (ммоль/л)
    """
    pack = models.ForeignKey(
        to='TestStripPack',
        on_delete=models.PROTECT,
        verbose_name='Пачка',
        related_name='meterings',
    )
    sugar_level = models.DecimalField(
        verbose_name='Уровень сахара в крови (ммоль/л)',
        max_digits=3,
        decimal_places=1,
    )

    def __str__(self):
        return '{} ммоль/л'.format(
            self.sugar_level)

    class Meta:
        verbose_name = 'Измерение сахара'
        verbose_name_plural = 'Измерения сахара'


class Comment(Attachment):
    content = models.CharField(
        max_length=400,
        verbose_name='Текст комментария',
    )

    def short(self, max_length=20, ending='<...>'):
        self.content: str
        result = self.content
        if len(self.content) > max_length:
            result = '{}{}'.format(
                self.content[:max_length - len(ending)],
                ending,
            )
        return result

    def __str__(self):
        return self.content

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'


class AbstractMedication(models.Model, AbleToVerbolizeDateTimeAttrsMixin):
    USAGES_MANAGER_NAME: Optional[str] = None
    
    class Meta:
        abstract = True

    whose = models.ForeignKey(
        to='auth.User',
        on_delete=models.CASCADE,
        related_name='+',
        verbose_name='Владелец',
    )

    volume = models.PositiveSmallIntegerField(
        verbose_name='Номинальный объём',
    )

    opening = models.DateField(
        verbose_name='Дата начала пользования',
    )

    expiry_plan = models.DateField(
        verbose_name='Плановая дата окончания пользования',
        blank=True,
        null=True,
    )

    expiry_actual = models.DateField(
        verbose_name='Фактическая дата окончания пользования',
        blank=True,
        null=True,
    )
    
    @classmethod
    def get_actual_items(cls, on_date: Optional[datetime]) -> models.QuerySet:
        if on_date is None:
            on_date = datetime.now()

        result = cls.objects.filter(
            models.Q(
                expiry_actual__isnull=True,
            ) | models.Q(
                expiry_actual__gte=on_date,
            ),
            opening__lte=on_date,
        )

        return result
    
    def is_expired(self) -> bool:
        return self.expiry_actual is not None
    is_expired.boolean = True
    is_expired.short_description = 'Израсходовано'

    def get_last_usage_moment(self) -> Optional[datetime]:
        usages_manager_name = self.__class__.USAGES_MANAGER_NAME

        assert usages_manager_name is not None

        return getattr(self, usages_manager_name).order_by(
            '-record__when',
        ).values_list(
            'record_when',
            flat=True,
        ).first()

    def get_used_amount(self) -> int:
        raise NotImplementedError

    def verbose_opening(self) -> str:
        return self.get_verbose_date(
            attr='opening',
        )
    verbose_opening.short_description = opening.verbose_name

    def verbose_expiry_plan(self) -> Optional[str]:
        return self.get_verbose_date(
            attr='expiry_plan',
        )
    verbose_expiry_plan.short_description = expiry_plan.verbose_name

    def verbose_expiry_actual(self) -> Optional[str]:
        return self.get_verbose_date(
            attr='expiry_actual',
        )
    verbose_expiry_actual.short_description = expiry_actual.verbose_name


class InsulinSyringe(AbstractMedication):
    USAGES_MANAGER_NAME = 'injections'

    class Meta:
        verbose_name = 'Шприц'
        verbose_name_plural = 'Шприцы'

    insulin_mark = models.ForeignKey(
        to=InsulinKind,
        verbose_name='Вид инсулина',
        on_delete=models.PROTECT,
    )

    def verbose_insulin_mark(self) -> str:
        return self.insulin_mark.name
    verbose_insulin_mark.short_description = insulin_mark.verbose_name

    def get_used_amount(self) -> int:
        return next(iter(self.injections.aggregate(
            used_amount=NumericSum(
                'insulin_quantity',
            ),
        ).values()))
    get_used_amount.short_description = 'Использовано'

    def __str__(self):
        return '{cls_name} "{insulin_mark}" ({volume} ед.) от {opening}'.format(  # noqa
            cls_name=self._meta.verbose_name,
            insulin_mark=str(self.insulin_mark),
            volume=str(self.volume),
            opening=self.verbose_opening(),
        )

    def __repr__(self):
        return (
            '<{cls_name}(\n'
            '    insulin_mark={insulin_mark},\n'
            '    volume={volume},\n'
            '    opening={opening},\n'
            '    expiry_plan={expiry_plan},\n'
            '    expiry_actual={expiry_actual},\n'
            ')>'
        ).format(
            cls_name=self.__class__.__name__,
            insulin_mark=repr(self.insulin_mark),
            volume=repr(self.volume),
            opening=repr(self.opening),
            expiry_plan=repr(self.expiry_plan),
            expiry_actual=repr(self.expiry_actual),
        )


class InsulinOrdering(models.Model, AbleToVerbolizeDateTimeAttrsMixin):
    class Meta:
        verbose_name = 'Выписка инсулина'
        verbose_name_plural = 'Выписки инсулина'

    whose = models.ForeignKey(
        to='auth.User',
        on_delete=models.CASCADE,
        related_name='+',
        verbose_name='Владелец',
    )

    insulin_mark = models.ForeignKey(
        to=InsulinKind,
        on_delete=models.PROTECT,
        related_name='+',
        verbose_name=InsulinKind._meta.verbose_name
    )

    when = models.DateField(
        verbose_name='Дата выписки',
    )
    next_ordering_plan_date = models.DateField(
        verbose_name='Планируемая дата следующей выписки',
        blank=True,
        null=True,
    )

    def verbose_when(self) -> Optional[str]:
        return self.get_verbose_date(
            attr='when',
        )
    verbose_when.short_description = when.verbose_name

    def verbose_insulin_mark(self) -> str:
        return self.insulin_mark.name
    verbose_insulin_mark.short_description = insulin_mark.verbose_name

    def __repr__(self):
        return '<{cls_name}(when={when})>'.format(
            cls_name=self.__class__.__name__,
            when=repr(self.when),
        )

    def __str__(self):
        return '{cls_name} от {when}'.format(
            cls_name=self._meta.verbose_name,
            when=self.verbose_when(),
        )


class TestStripPack(AbstractMedication):
    class Meta:
        verbose_name = 'Пачка тест-полосок'
        verbose_name_plural = 'Пачки тест-полосок'

    def get_used_amount(self) -> int:
        return self.meterings.count()
    get_used_amount.short_description = 'Использовано'

    def __repr__(self):
        return (
            '<{cls_name}(\n'
            '    volume={volume},\n'
            '    opening={opening},\n'
            '    expiry_plan={expiry_plan},\n'
            '    expiry_actual={expiry_actual},\n'
            ')>'
        ).format(
            cls_name=self.__class__.__name__,
            insulin_mark=repr(self.insulin_mark),
            volume=repr(self.volume),
            opening=repr(self.opening),
            expiry_plan=repr(self.expiry_plan),
            expiry_actual=repr(self.expiry_actual),
        )

    def __str__(self):
        return '{cls_name} от {when}'.format(
            cls_name=self._meta.verbose_name,
            when=self.verbose_opening(),
        )
