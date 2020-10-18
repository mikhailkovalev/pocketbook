from django.contrib import admin


# class OwnableModelAdmin(admin.ModelAdmin):
#

def ownable(owner_field: str):

    def get_queryset(self, request):
        queryset = super(self.__class__, self).get_queryset(request)

        queryset = queryset.filter(
            **{f'{owner_field}_id': request.user.id},
        )

        return queryset

    def save_model(self, request, obj, form, change):
        setattr(obj, owner_field, request.user)
        super(self.__class__, self).save_model(request, obj, form, change)

    def decorator(cls):
        cls.get_queryset = get_queryset
        cls.save_model = save_model
        return cls

    return decorator
