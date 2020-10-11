from django.contrib import (
    admin,
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

admin.site.register(InsulinKind)


class MealInline(admin.TabularInline):
    model = Meal
    extra = 1


class InsulinInjectionInline(admin.TabularInline):
    model = InsulinInjection
    extra = 1

    def get_field_queryset(self, db, db_field, request):
        queryset = super().get_field_queryset(db, db_field, request)

        if db_field is self.model._meta.get_field('insulin_mark'):
            if queryset is None:
                queryset = db_field.related_model.objects.all()

            mark_ids = InsulinSyringe.objects.filter(
                expiry_actual__isnull=True,
            ).values_list(
                'insulin_mark',
                flat=True,
            )
            filtered_queryset = queryset.filter(
                pk__in=mark_ids,
            )
            if filtered_queryset.exists():
                queryset = filtered_queryset

        return queryset


class SugarMeteringInline(admin.TabularInline):
    model = SugarMetering
    extra = 1


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 1
    form = CommentForm


@admin.register(Record)
class RecordAdmin(admin.ModelAdmin):
    """
    Класс админки для записи дневника.
    """
    list_display = (
        'when_verbose',
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

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.filter(
            who_id=request.user.id)
        return queryset

    def save_model(self, request, obj, form, change):
        obj.who = request.user
        super().save_model(request, obj, form, change)


@admin.register(InsulinSyringe)
class InsulinSyringeAdmin(admin.ModelAdmin):
    list_display = (
        'verbose_insulin_mark',
        'volume',
        'is_expired',
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

    def get_queryset(self, request):
        queryset = super().get_queryset(request)

        queryset = queryset.filter(
            whose_id=request.user.id,
        )

        return queryset

    def save_model(self, request, obj, form, change):
        obj.whose = request.user
        super().save_model(request, obj, form, change)


@admin.register(InsulinOrdering)
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

    def get_queryset(self, request):
        queryset = super().get_queryset(request)

        queryset = queryset.filter(
            whose_id=request.user.id,
        )

        return queryset

    def save_model(self, request, obj, form, change):
        obj.whose = request.user
        super().save_model(request, obj, form, change)


@admin.register(TestStripPack)
class TestStripPackAdmin(admin.ModelAdmin):
    list_display = (
        '__str__',
        'volume',
        'is_expired',
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

    def get_queryset(self, request):
        queryset = super().get_queryset(request)

        queryset = queryset.filter(
            whose_id=request.user.id,
        )

        return queryset

    def save_model(self, request, obj, form, change):
        obj.whose = request.user
        super().save_model(request, obj, form, change)
