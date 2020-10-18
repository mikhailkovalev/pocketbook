from typing import (
    Any,
    Dict,
    Optional,
)

from django.db.models import (
    Model,
)
from mptt.admin import (
    MPTTModelAdmin,
)


class HierarchicalAdmin(MPTTModelAdmin):
    hierarchy_cls: Optional[Model] = None

    @classmethod
    def _own_records_filter(cls, request, queryset):
        if not hasattr(cls.hierarchy_cls, 'get_own_items_ids'):
            raise TypeError

        own_ids = cls.hierarchy_cls.get_own_items_ids(
            owner_id=request.user.id,
        )
        queryset = queryset.filter(
            pk__in=own_ids,
        )
        return queryset

    def get_queryset(self, request):
        queryset = super().get_queryset(request)

        if queryset.model._hierarchical_meta.ownable:
            queryset = self._own_records_filter(request, queryset)

        return queryset
    
    def get_field_queryset(self, db, db_field, request):
        queryset = super().get_field_queryset(db, db_field, request)
        
        parent_attr = queryset.model._mptt_meta.parent_attr

        is_parent_field = db_field is self.model._meta.get_field(parent_attr)
        model_is_ownable = queryset.model._hierarchical_meta.ownable

        if is_parent_field and model_is_ownable:
            queryset = self._own_records_filter(request, queryset)

        return queryset

    def save_model(self, request, obj, form, change):
        parent_attr = obj._mptt_meta.parent_attr
        create_hierarchy = not obj.id and not getattr(obj, parent_attr)

        result = super().save_model(request, obj, form, change)

        if create_hierarchy:
            meta = obj._hierarchical_meta

            create_kwargs: Dict[str, Any] = {
                meta.root_attr: obj,
            }
            if meta.ownable:
                create_kwargs[meta.owner_attr] = request.user

            self.hierarchy_cls.objects.create(
                **create_kwargs,
            )

        return result
