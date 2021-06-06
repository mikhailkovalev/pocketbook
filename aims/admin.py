from django.contrib import (
    admin,
)

from core.hierarchical.admin import (
    HierarchicalAdmin,
)

from .models import (
    Action,
    Aim,
    AimHierarchy,
)


class ActionInline(admin.TabularInline):
    model = Action
    extra = 1
    fields = (
        'when',
        'elapsed_time',
        'description',
    )
    ordering = (
        'when',
    )


@admin.register(Aim)
class AimAdmin(HierarchicalAdmin):
    hierarchy_cls = AimHierarchy

    list_display = (
        'name',
        'done',
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
    inlines = (
        ActionInline,
    )


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

    @staticmethod
    def get_own_aims_ids(owner_id):
        return AimHierarchy.get_own_items_ids(
            owner_id=owner_id,
        )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)

        own_ids = self.get_own_aims_ids(
            owner_id=request.user.id,
        )
        queryset = queryset.filter(
            aim__in=own_ids,
        )

        return queryset

    def get_field_queryset(self, db, db_field, request):
        queryset = super().get_field_queryset(db, db_field, request)

        if db_field is self.model._meta.get_field('aim'):  # noqa
            own_aim_ids = self.get_own_aims_ids(
                owner_id=request.user.id,
            )
            queryset = db_field.related_model._default_manager.filter(  # noqa
                pk__in=own_aim_ids,
                done=False,
            )

        return queryset
