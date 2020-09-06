from core.enums import (
    BaseEnumerate,
)


class AccountActivityEnum(BaseEnumerate):
    ACTIVE = 'active'
    PASSIVE = 'passive'
    INCOME = 'income'
    EXPENSE = 'expense'

    values = {
        ACTIVE: 'Активный',
        PASSIVE: 'Пассивный',
        INCOME: 'Приход',
        EXPENSE: 'Расход',
    }
