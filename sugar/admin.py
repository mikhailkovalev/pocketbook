import logging

from django.contrib import (
    admin,
)
from django.contrib.admin.views.main import ChangeList

from core.admin import (
    ownable,
)
from core.helpers import (
    get_datetime_display,
    track_time,
    with_server_timezone,
)

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

logger = logging.getLogger(__name__)

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


class RecordAdminChangeList(ChangeList):
    def get_results(self, request):
        with track_time() as tracker:
            results = super().get_results(request)
        logger.debug(
            '%r elapsed time: %.3fsec',
            f'{type(self).__name__}.get_results',
            tracker.elapsed_time,
        )
        return results


@admin.register(Record)
@ownable('who')
class RecordAdmin(admin.ModelAdmin):
    """
    Класс админки для записи дневника.
    """
    list_display = (
        'get_when_display',
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

    def get_when_display(self, obj: Record):
        localized_when = with_server_timezone(obj.when)
        return get_datetime_display(localized_when)
    get_when_display.short_description = 'when'

    def get_changelist(self, request, **kwargs):
        return RecordAdminChangeList


@admin.register(InsulinSyringe)
@ownable('whose')
class InsulinSyringeAdmin(admin.ModelAdmin):
    list_display = (
        'get_insulin_mark_name',
        'volume',
        'is_expired',
        'get_used_amount',
        'get_opening_display',
        'get_expiry_plan_display',
        'get_expiry_actual_display',
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
        'get_insulin_mark_name',
        'get_when_display',
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
        'get_expiry_plan_display',
        'get_expiry_actual_display',
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
