from collections import defaultdict
from datetime import datetime

from django.db import models

from core.datetime_helpers import (
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

    def meal_info(self):
        meals = Meal.objects.filter(
            record=self.pk
        )
        if meals.count() == 0:
            return

        return '+'.join(map(str, meals.values_list(
            'food_quantity',
            flat=True,
        )))

    def injections_info(self):
        injections = InsulinInjection.objects.filter(
            record=self.pk
        )
        if injections.count() == 0:
            return

        injections_by_kind = defaultdict(list)
        injections = injections.values_list(
            'insulin_mark__name',
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
    food_quantity = models.DecimalField(
        verbose_name='Количество употреблённых углеводов (ХЕ)',
        max_digits=3,
        decimal_places=1,
    )

    def __str__(self):
        return '{}: {}ХЕ'.format(
            self.__class__.__name__,
            self.food_quantity,
        )

    class Meta:
        verbose_name = 'Приём пищи'
        verbose_name_plural = 'Приёмы пищи'


class InsulinKind(models.Model):
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
    insulin_mark = models.ForeignKey(
        to=InsulinKind,
        verbose_name='Вид инсулина',
        on_delete=models.PROTECT,
    )
    insulin_quantity = models.PositiveSmallIntegerField(
        verbose_name='Количество введённого инсулина',
        null=True,
    )

    def __str__(self):
        return 'Инъекция({}): {}ед.'.format(
            self.insulin_mark.name,
            self.insulin_quantity,
        )

    class Meta:
        verbose_name = 'Инъекция инсулина'
        verbose_name_plural = 'Инъекции инсулина'


class SugarMetering(Attachment):
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
