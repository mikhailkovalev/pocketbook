from django import forms

from .models import Comment


class CommentForm(forms.ModelForm):
    content = forms.CharField(
        widget=forms.Textarea,
    )

    class Meta:
        model = Comment
        fields = (
            'content',
        )
