from django.contrib import (
    admin,
)

from .models import (
    Action,
    Aim,
)


@admin.register(Aim)
class AimAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'created',
        'estimated_time',
        'elapsed_time',
    )
    fields = (
        'name',
        'created',
        'estimated_time',
    )


@admin.register(Action)
class ActionAdmin(admin.ModelAdmin):
    list_display = (
        'when',
        'aim',
        'elapsed_time',
        'short_description',
    )
    fields = (
        'when',
        'aim',
        'elapsed_time',
        'description',
    )
