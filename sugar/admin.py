from django.contrib import admin

from .models import (
    Meal, InsulinKind, InsulinInjection,
    SugarMetering, Record,
)


admin.site.register(InsulinKind)


class MealInline(admin.TabularInline):
    model = Meal
    extra = 1


class InsulinInjectionInline(admin.TabularInline):
    model = InsulinInjection
    extra = 1


class SugarMeteringInline(admin.TabularInline):
    model = SugarMetering
    extra = 1


@admin.register(Record)
class RecordAdmin(admin.ModelAdmin):
    """
    Класс админки для записи дневника.
    """
    list_display = (
        'when_verbose',
        'sugar_level',
        'meal_info',
        'injections_info',
    )
    inlines = (
        SugarMeteringInline,
        MealInline,
        InsulinInjectionInline,
    )
