from collections import defaultdict
from decimal import Decimal
from typing import Optional

from django.contrib import (
    admin,
)

from core.admin import (
    ownable,
)
from core.helpers import get_verbose_datetime, with_server_timezone

from .forms import (
    CommentForm,
)
from .models import (
    Comment,
    InsulinInjection,
    InsulinKind,
    InsulinOrdering,
    InsulinSyringe,
    Meal,
    Record,
    SugarMetering,
    TestStripPack,
)

admin.site.register(InsulinKind)


class MealInline(admin.TabularInline):
    model = Meal
    extra = 1


class InsulinInjectionInline(admin.TabularInline):
    model = InsulinInjection
    extra = 1

    def get_field_queryset(self, db, db_field, request):
        queryset = super().get_field_queryset(db, db_field, request)

        insylin_syringe_field_name = 'insulin_syringe'

        if db_field is self.model._meta.get_field(insylin_syringe_field_name):
            record_id = request.resolver_match.kwargs.get('object_id')
            actual_moment = self.model._meta.get_field(
                'record',
            ).related_model.objects.filter(
                pk=record_id,
            ).values_list(
                'when',
                flat=True,
            ).first()
            queryset = self.model._meta.get_field(
                insylin_syringe_field_name,
            ).related_model.get_actual_items(
                on_date=actual_moment,
            )

        return queryset


class SugarMeteringInline(admin.TabularInline):
    model = SugarMetering
    extra = 1

    def get_field_queryset(self, db, db_field, request):
        queryset = super().get_field_queryset(db, db_field, request)
        
        pack_field_name = 'pack'

        if db_field is self.model._meta.get_field(pack_field_name):
            record_id = request.resolver_match.kwargs.get('object_id')
            actual_moment = self.model._meta.get_field(
                'record',
            ).related_model.objects.filter(
                pk=record_id,
            ).values_list(
                'when',
                flat=True,
            ).first()
            queryset = self.model._meta.get_field(
                pack_field_name,
            ).related_model.get_actual_items(
                on_date=actual_moment,
            )

        return queryset


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 1
    form = CommentForm


@admin.register(Record)
@ownable('who')
class RecordAdmin(admin.ModelAdmin):
    """
    Класс админки для записи дневника.
    """
    list_display = (
        'when_display',
        'sugar_level',
        'total_meal',
        'injections_info',
        'short_comments',
    )
    fields = (
        'when',
    )
    inlines = (
        SugarMeteringInline,
        MealInline,
        InsulinInjectionInline,
        CommentInline,
    )

    # noinspection PyMethodMayBeStatic
    def when_display(self, obj: Record) -> str:
        localized_when = with_server_timezone(obj.when)
        return get_verbose_datetime(localized_when)

    # noinspection PyMethodMayBeStatic
    def sugar_level(self, obj: Record) -> Optional[Decimal]:
        try:
            sugar_metering = obj.sugarmetering
        except SugarMetering.DoesNotExist:
            return None

        return sugar_metering.sugar_level

    # noinspection PyMethodMayBeStatic
    def total_meal(self, obj: Record) -> Optional[Decimal]:
        meals = obj.meal_set.all()

        meals_count = len(meals)
        if meals_count == 0:
            return None
        else:
            return sum(meal.food_quantity for meal in meals)
    
    # noinspection PyMethodMayBeStatic
    def injections_info(self, obj: Record) -> Optional[str]:
        injections = obj.insulininjection_set.all()

        injections_count = len(injections)
        if injections_count == 0:
            return None
        else:
            injections_by_kind = defaultdict(list)

            injection: InsulinInjection
            for injection in injections:
                kind = injection.insulin_syringe.insulin_mark.name
                injections_by_kind[kind].append(injection.insulin_quantity)

            return ', '.join(
                '{} {}'.format('+'.join(map(str, quantities)), kind)
                for kind, quantities in injections_by_kind.items()
            )

    # noinspection PyMethodMayBeStatic
    def short_comments(self, obj: Record) -> Optional[str]:
        comments = obj.comment_set.all()

        short_comments = [
            comment.short()
            for comment in comments
        ]

        if not short_comments:
            return None
        else:
            return '; '.join(short_comments)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related(
            'sugarmetering',
        ).prefetch_related(
            'meal_set',
            'insulininjection_set__insulin_syringe__insulin_mark',
            'comment_set',
        )


@admin.register(InsulinSyringe)
@ownable('whose')
class InsulinSyringeAdmin(admin.ModelAdmin):
    list_display = (
        'verbose_insulin_mark',
        'volume',
        'is_expired',
        'get_used_amount',
        'verbose_opening',
        'verbose_expiry_plan',
        'verbose_expiry_actual',
    )
    fields = (
        'insulin_mark',
        'volume',
        'opening',
        'expiry_plan',
        'expiry_actual',
    )
    ordering = (
        '-opening',
    )


@admin.register(InsulinOrdering)
@ownable('whose')
class InsulinOrderingAdmin(admin.ModelAdmin):
    list_display = (
        'verbose_insulin_mark',
        'verbose_when',
        'next_ordering_plan_date',
    )
    fields = (
        'insulin_mark',
        'when',
        'next_ordering_plan_date',
    )
    ordering = (
        '-when',
    )


@admin.register(TestStripPack)
@ownable('whose')
class TestStripPackAdmin(admin.ModelAdmin):
    list_display = (
        '__str__',
        'volume',
        'is_expired',
        'get_used_amount',
        'verbose_expiry_plan',
        'verbose_expiry_actual',
    )
    fields = (
        'volume',
        'opening',
        'expiry_plan',
        'expiry_actual',
    )
    ordering = (
        '-opening',
    )
