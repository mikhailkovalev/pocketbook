from core.enums import (
    BaseEnumerate,
)


class AccountActivityEnum(BaseEnumerate):
    ACTIVE = 'active'
    PASSIVE = 'passive'

    values = {
        ACTIVE: 'Активный',
        PASSIVE: 'Пассивный',
    }


class TransferDirectionEnum(BaseEnumerate):
    DEBIT = 'debit'
    CREDIT = 'credit'

    values = {
        DEBIT: 'Дебет',
        CREDIT: 'Кредит',
    }
