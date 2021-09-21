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
