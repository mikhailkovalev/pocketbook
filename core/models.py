import string

from django.db import (
    models,
)


class Hierarchical(models.Model):
    ALLOWED_CHARACTERS = ''.join((
        string.digits,
        string.ascii_letters,
    ))

    class Meta:
        abstract = True
