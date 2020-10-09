from django.contrib import (
    admin,
)
from mptt.admin import (
    MPTTModelAdmin,
)

from .models import (
    Action,
    Aim,
)


@admin.register(Aim)
class AimAdmin(MPTTModelAdmin):
    list_display = (
        'name',
        'verbose_created',
        'verbose_deadline',
        'estimated_time',
        'elapsed_time',
    )
    fields = (
        'parent',
        'name',
        'done',
        'created',
        'deadline',
        'estimated_time',
        'description',
    )

    @staticmethod
    def _own_records_filter(request, queryset):
        own_ids = queryset.model.get_own_ids(
            owner_id=request.user.id,
        )
        queryset = queryset.filter(
            pk__in=own_ids,
        )
        return queryset

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return self._own_records_filter(request, queryset)

    def get_field_queryset(self, db, db_field, request):
        queryset = super().get_field_queryset(db, db_field, request)

        if db_field is self.model._meta.get_field('parent'):
            queryset = self._own_records_filter(request, queryset)

        return queryset

    def save_model(self, request, obj, form, change):
        create_hierarchy = not obj.id

        result = super().save_model(request, obj, form, change)

        if create_hierarchy:
            self.model.aimhierarchy.related.related_model.objects.create(
                root=obj,
                whose=request.user,
            )

        return result


@admin.register(Action)
class ActionAdmin(admin.ModelAdmin):
    list_display = (
        'verbose_when',
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
    ordering = (
        '-when',
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)

        own_ids = Aim.get_own_ids(
            owner_id=request.user.id,
        )
        queryset = queryset.filter(
            aim__in=own_ids,
        )

        return queryset

    def get_field_queryset(self, db, db_field, request):
        queryset = super().get_field_queryset(db, db_field, request)

        if db_field is self.model._meta.get_field('aim'):
            own_aim_ids = db_field.related_model.get_own_ids(
                owner_id=request.user.id,
            )
            queryset = db_field.related_model._default_manager.filter(
                pk__in=own_aim_ids,
            )

        return queryset
