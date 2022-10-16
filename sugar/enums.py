from django.db.models import TextChoices


class DateAggregateEnum(TextChoices):
    NONE = ('none', 'Без группировки')
    DAY = ('day', 'По дням')
    WEEK = ('week', 'По неделям')
    MONTH = ('month', 'По месяцам')
    YEAR = ('year', 'По годам')
