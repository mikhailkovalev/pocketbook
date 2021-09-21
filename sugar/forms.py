from django import (
    forms,
)
from sugar.enums import (
    DateAggregateEnum,
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
    groupping = forms.ChoiceField(
        label='Группировка',
        choices=DateAggregateEnum.get_choices(),
        initial=DateAggregateEnum.DAY,
    )
    page_number = forms.IntegerField(
        label='Страница',
        min_value=1,
        initial=1,
    )
