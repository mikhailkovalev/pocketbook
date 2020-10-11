from django.core.exceptions import (
    ValidationError,
)
from django.db import (
    models,
)

from mptt.models import (
    MPTTModel,
    TreeOneToOneField,
)

from core.helpers import (
    with_server_timezone,
)
from core.hierarchical.models import (
    Hierarchical,
)

from .enums import (
    AccountActivityEnum,
)

# todo: Проверка целостности данных в базе:
#  - для каждого счёта, его родитель и его корень и,
#    привязанный к нему, объект иерархии ссылаются на
#    одного и того же пользователя
#  - для каждого счёта его родительские связи
#    действительно восходят к его корню.
#  - Сумма произведения количества на цену всех
#    TransferDetail-ов привязанных к Transfer-у должна
#    быть равна сумме, указанной в Transfer-е.


class Account(Hierarchical):
    """
    Счёт, на котором хранятся средства.

    Если счёт активный, то положительное значение на
    этом счету говорит о принадлежности этих средств
    пользователю. Если счёт пассивный, то
    положительное значение на этом счету говорит о
    задолженности пользователя.
    """

    name = models.CharField(
        unique=True,
        verbose_name='Наименование',
        max_length=50,
    )

    class Meta:
        verbose_name = 'Счёт'
        verbose_name_plural = 'Счета'

    def __str__(self):
        return self.name

    @property
    def activity(self):
        return self.get_ancestors(
            include_self=True,
        ).filter(
            parent__isnull=True,
        ).values_list(
            'accounthierarchy__activity',
            flat=True,
        ).get()

    @property
    def verbose_activity(self):
        return AccountActivityEnum.values[self.activity]


AccountHierarchyBase = Account.get_hierarchy_cls()


class AccountHierarchy(AccountHierarchyBase):
    """
    Иерархия счетов

    Каждый пользователь может иметь собственную
    иерархию источников и назначений платежей.
    """
    activity = models.CharField(
        max_length=8,
        choices=AccountActivityEnum.get_choices(),
        verbose_name='Тип счёта',
    )

    class Meta:
        verbose_name = 'Иерархия счетов'
        verbose_name_plural = 'Иерархии счетов'
        unique_together = (
            (
                'whose',
                'activity',
            ),
        )

    @property
    def verbose_activity(self) -> str:
        return AccountActivityEnum.values[self.activity]

    def __repr__(self):
        return '<{model_name}(activity=\'{activity}\', whose={user})>'.format(
            model_name=self.__class__.__name__,
            activity=self.activity,
            user=repr(self.whose),
        )

    def __str__(self):
        return self.verbose_activity

    def clean(self):
        if self.root.parent is not None:
            raise ValidationError(
                message='Корневой элемент иерархии не должен иметь родительского!',  # noqa
            )


class BalanceFixation(MPTTModel):
    """
    Модель фиксации остатков средств на счетах.
    """
    when = models.DateTimeField(
        verbose_name='Момент фиксации',
    )
    prev_fixation = TreeOneToOneField(
        to='self',
        on_delete=models.PROTECT,
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
        super().clean()
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
            (
                'account',
                'fixation',
            ),
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


class Provider(Hierarchical):
    """
    Источник/получатель платежа
    """
    name = models.CharField(
        unique=True,
        max_length=100,
        verbose_name='Наименование',
    )

    class Meta:
        verbose_name = 'Источник/получатель платежа'
        verbose_name_plural = 'Источники/получатели платежей'


ProviderHierarchyBase = Provider.get_hierarchy_cls()


class ProviderHierarchy(ProviderHierarchyBase):
    class Meta:
        verbose_name = 'Иерархия провайдеров'
        verbose_name_plural = 'Иерархии провайдеров'


class Transfer(models.Model):
    """
    Перевод средств.

    Операция должна происходить между фиксацией,
    указанной в поле `fixation` и той, что ей
    предшествует.
    """
    when = models.DateField(
        verbose_name='Дата операции',
    )
    fixation = models.ForeignKey(
        to=BalanceFixation,
        on_delete=models.SET_NULL,
        null=True,
        related_name='transfers',
        verbose_name='Фиксация, в которой учтена эта операция',
    )
    debit_account = models.ForeignKey(
        to=Account,
        on_delete=models.PROTECT,
        related_name='debit_transfers',
        verbose_name='Счёт зачисления',
    )
    credit_account = models.ForeignKey(
        to=Account,
        on_delete=models.PROTECT,
        related_name='credit_transfers',
        verbose_name='Счёт списания',
    )
    value = models.DecimalField(
        verbose_name='Сумма операции',
        max_digits=15,
        decimal_places=2,
    )
    provider = models.ForeignKey(
        to=Provider,
        on_delete=models.PROTECT,
        null=True,
        verbose_name='Источник/получатель платежа',
    )

    class Meta:
        verbose_name = 'Операция'
        verbose_name_plural = 'Операции'
        ordering = (
            '-when',
        )

    def clean(self):
        super().clean()
        # todo: проверить, что дата платежа находится
        #  в допустимом интервале между фиксациями


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
    name = models.CharField(
        verbose_name='Наименование',
        max_length=50,
    )
    count = models.DecimalField(
        verbose_name='Количество товара/услуг',
        max_digits=15,
        decimal_places=3,
    )
    cost = models.DecimalField(
        verbose_name='Цена за единицу',
        max_digits=15,
        decimal_places=2,
    )

    class Meta:
        verbose_name = 'Деталь операции'
        verbose_name_plural = 'Детали операций'
