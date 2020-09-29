from django.db.models import (
    Manager,
)

from mptt.managers import (
    TreeManager,
)

from .querysets import (
    HierarchicalQuerySet,
)


class HierarchicalManager(
    Manager.from_queryset(HierarchicalQuerySet),
    TreeManager,
):
    pass
