from django.contrib import (
    admin,
)

from mptt.admin import (
    MPTTModelAdmin,
)

from .models import (
    Account,
    AccountHierarchy,
)


@admin.register(AccountHierarchy)
class AccountHierarchyAdmin(admin.ModelAdmin):
    pass


@admin.register(Account)
class AccountAdmin(MPTTModelAdmin):
    list_display = (
        'name',
        'verbose_activity',
        # todo: last fixed balance
    )
    fields = (
        'parent',
        'name',
    )
