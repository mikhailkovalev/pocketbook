def ownable(owner_field: str):

    def decorator(cls):
        class OwnableAdmin(cls):
            def get_queryset(self, request):
                queryset = super().get_queryset(request)

                queryset = queryset.filter(
                    **{owner_field: request.user},
                )

                return queryset

            def save_model(self, request, obj, form, change):
                setattr(obj, owner_field, request.user)
                super().save_model(request, obj, form, change)

        return OwnableAdmin

    return decorator
