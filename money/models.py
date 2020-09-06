from django.core.exceptions import (
    ValidationError,
)
from django.db import (
    models,
)

from core.helpers import (
    with_server_timezone,
)

from .enums import (
    AccountActivityEnum,
    TransferDirectionEnum,
)


class Account(models.Model):
    """
    Счёт, на котором хранятся средства.

    Если счёт активный, то положительное значение на
    этом счету говорит о принадлежности этих средств
    пользователю. Если счёт пассивный, то
    положительное значение на этом счету говорит о
    задолженности пользователя.
    """

    whose = models.ForeignKey(
        to='auth.User',
        on_delete=models.CASCADE,
        related_name='accounts',
        verbose_name='Владелец',
    )
    activity = models.CharField(
        max_length=8,
        choices=AccountActivityEnum.get_choices(),
    )
    name = models.CharField(
        unique=True,
        verbose_name='Наименование',
        max_length=50,
    )

    class Meta:
        verbose_name = 'Счёт'
        verbose_name_plural = 'Счета'

    def __str__(self):
        return f'{self.name} ({AccountActivityEnum.values[self.activity]})'


class BalanceFixation(models.Model):
    """
    Модель фиксации остатков средств на счетах.
    """
    when = models.DateTimeField(
        verbose_name='Момент фиксации',
    )
    prev_fixation = models.OneToOneField(
        to='self',
        on_delete=models.CASCADE,
        null=True,
        related_name='next_fixation',
        verbose_name='Предыдущая фиксация',
    )

    class Meta:
        verbose_name = 'Фиксация остатков'
        verbose_name_plural = 'Фиксации остатков'
        ordering = (
            '-when',
        )

    def __str__(self):
        verbose_when = with_server_timezone(
            self.when,
        ).strftime(
            '%Y-%m-%d %H:%M',
        )
        return f'{self._meta.verbose_name} от {verbose_when}'

    def clean(self):
        account_owners_count = len(set(self.balance_set.values_list(
            'account__whose_id',
            flat=True,
        )))
        if account_owners_count > 1:
            raise ValidationError(
                message='В фиксации использованы счета разных пользователей!',
            )


class Balance(models.Model):
    """
    Остаток средств на указанном счёте в момент
    фиксации.
    """
    account = models.ForeignKey(
        to=Account,
        on_delete=models.CASCADE,
        verbose_name='Счёт',
    )
    fixation = models.ForeignKey(
        to=BalanceFixation,
        on_delete=models.CASCADE,
        verbose_name='Фиксация',
    )
    value = models.DecimalField(
        verbose_name='Остаток',
        max_digits=15,
        decimal_places=2,
    )

    class Meta:
        unique_together = (
            ('account', 'fixation'),
        )
        verbose_name = 'Остаток средств'
        verbose_name_plural = 'Остатки средств'

    def __str__(self):

        result = '{fixation}. {name}: {value}'.format(
            fixation=self.fixation,
            name=self.account,
            value=self.value,
        )
        return result


class TransferReason(models.Model):
    """
    Назначение расхода или источник прихода.

    Имеет иерархическую структуру: запись "Кофе" может
    ссылаться на запись "Напитки" как на родительскую.
    """
    name = models.CharField(
        verbose_name='Описание',
        max_length=50,
    )
    parent = models.ForeignKey(
        to='self',
        null=True,
        on_delete=models.PROTECT,
        related_name='children',
        verbose_name='Обобщение',
    )

    class Meta:
        verbose_name = 'Источник/назначение'
        verbose_name_plural = 'Источники/назначения'

    def __str__(self):
        return self.name


class TransferReasonHierarchy(models.Model):
    """
    Иерархия назначений/источников расходов/доходов.

    Каждый пользователь может иметь собственную
    иерархию источников и назначений платежей.
    """
    whose = models.OneToOneField(
        to='auth.User',
        on_delete=models.CASCADE,
        related_name='transfer_reason_hierarchy',
        verbose_name='Владелец иерархии',
    )
    root = models.OneToOneField(
        to=TransferReason,
        on_delete=models.CASCADE,
        verbose_name='Корневой элемент иерархии',
    )

    class Meta:
        verbose_name = 'Иерархия назначений расходов/источников доходов'
        verbose_name_plural = 'Иерархии назначений расходов/источников доходов'

    def clean(self):
        if self.root.parent is not None:
            raise ValidationError(
                message='Корневой элемент иерархии не должен иметь родительского!',  # noqa
            )


class Transfer(models.Model):
    """
    Приход/расход.

    Операция должна происходить между фиксацией,
    указанной в поле `fixation` и той, что ей
    предшествует.

    Активный счёт:
        дебет: приход (увеличивает капитал)
        кредит: расход (уменьшает капитал)
    Пассивный счёт:
        дебет: расход (увеличивает задолженность)
        кредит: приход (уменьшает задолженность)
    """
    when = models.DateTimeField(
        verbose_name='Дата операции',
    )
    account = models.ForeignKey(
        to=Account,
        on_delete=models.PROTECT,
        related_name='transfers',
        verbose_name='Счёт списания/зачисления',
    )
    fixation = models.ForeignKey(
        to=BalanceFixation,
        on_delete=models.SET_NULL,
        null=True,
        related_name='transfers',
        verbose_name='Фиксация, в которой учтена эта операция',
    )
    direction = models.CharField(
        verbose_name='Дебет/кредит',
        max_length=7,
        choices=TransferDirectionEnum.get_choices(),
    )
    value = models.DecimalField(
        verbose_name='Сумма операции',
        max_digits=15,
        decimal_places=2,
    )
    provider = models.CharField(
        verbose_name='Источник/получатель платежа',
        max_length=50,
    )

    class Meta:
        verbose_name = 'Операция'
        verbose_name_plural = 'Операции'
        ordering = (
            '-when',
        )


class TransferDetail(models.Model):
    """
    Деталь операции.

    Как пример -- позиция в чеке. Разные позиции
    одного и того же чека могут иметь разные
    назначения.
    """
    transfer = models.ForeignKey(
        to=Transfer,
        on_delete=models.CASCADE,
        related_name='details',
        verbose_name='Операция',
    )
    reason = models.ForeignKey(
        to=TransferReason,
        on_delete=models.PROTECT,
    )
    count = models.DecimalField(
        verbose_name='Количество товара/услуг',
        max_digits=15,
        decimal_places=3,
    )
    value = models.DecimalField(
        verbose_name='Сумма позиции',
        max_digits=15,
        decimal_places=2,
    )

    class Meta:
        verbose_name = 'Деталь операции'
        verbose_name_plural = 'Детали операций'
