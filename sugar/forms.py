from django import (
    forms,
)
from sugar.enums import (
    DateAggregateEnum,
    PeriodEnum,
)

from .models import (
    Comment,
)


class CommentForm(forms.ModelForm):
    content = forms.CharField(
        widget=forms.Textarea,
    )

    class Meta:
        model = Comment
        fields = (
            'content',
        )


class ListViewForm(forms.Form):
    period = forms.ChoiceField(
        label='Период',
        choices=PeriodEnum.get_choices(),
        initial=PeriodEnum.WEEK,
    )
    groupping = forms.ChoiceField(
        label='Группировка',
        choices=DateAggregateEnum.get_choices(),
        initial=DateAggregateEnum.DAY,
    )
