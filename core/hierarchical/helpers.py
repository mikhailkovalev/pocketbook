def get_own_items_ids(cls, owner_id):
    root_attr = cls._hierarchical_meta.root_attr

    roots_ids = cls.objects.filter(
        whose_id=owner_id,
    ).values_list(
        f'{root_attr}_id',
        flat=True,
    )

    related_model = cls._meta.get_field(root_attr).related_model

    return related_model.objects.filter(
        pk__in=roots_ids,
    ).get_descendants(
        include_self=True,
    ).values_list(
        'pk',
        flat=True,
    )
