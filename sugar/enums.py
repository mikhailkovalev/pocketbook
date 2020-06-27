from core.enums import BaseEnumerate


class DateAggregateEnum(BaseEnumerate):
    NONE = 'none'
    DAY = 'day'
    WEEK = 'week'
    MONTH = 'month'
    YEAR = 'year'

    values = {
        NONE: 'Без группировки',
        DAY: 'По дням',
        WEEK: 'По неделям',
        MONTH: 'По месяцам',
        YEAR: 'По годам',
    }


class PeriodEnum(BaseEnumerate):
    NONE = 'none'
    TODAY = 'today'
    TWO_DAYS = 'two_days'
    WEEK = 'week'
    MONTH = 'month'
    CUSTOM = 'custom'

    values = {
        NONE: 'Без периода',
        TODAY: 'Сегодня',
        TWO_DAYS: 'Вчера и сегодня',
        WEEK: 'Последние семь дней',
        MONTH: 'Последние 30 дней',
    }