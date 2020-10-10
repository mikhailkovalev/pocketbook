from typing import (
    Dict,
    Iterator,
    NamedTuple,
    Optional,
)

from django.contrib.auth.models import (
    User,
)
from django.core.management import (
    BaseCommand,
    CommandParser,
)

from core.helpers import (
    iterate_csv_by_namedtuples,
)

from money.models import (
    Provider,
    ProviderHierarchy,
)


class RowType(NamedTuple):
    name: str
    parent: str


class Command(BaseCommand):

    def add_arguments(self, parser: CommandParser):
        super().add_arguments(parser)
        parser.add_argument(
            'username',
        )
        parser.add_argument(
            'file_path',
        )

    def handle(self, username, file_path, *args, **options):
        user_id = User.objects.filter(
            username=username,
        ).values_list(
            'id',
            flat=True,
        ).get()

        source = open(file_path, 'rt', encoding='utf-8')
        items: Iterator[RowType] = iterate_csv_by_namedtuples(
            source,
            rowtype=RowType,
            delimiter=';',
        )

        providers_by_name: Dict[str, Provider] = {}

        for item in items:

            parent: Optional[Provider] = None
            if item.parent:
                try:
                    parent = providers_by_name[item.parent]
                except KeyError:
                    raise ValueError(
                        'You have to define provider "{parent}" before using it with account "{name}"'.format(  # noqa
                            parent=item.parent,
                            name=item.name,
                        ),
                    )

            provider = Provider.objects.create(
                name=item.name,
                parent=parent,
            )
            providers_by_name[item.name] = provider

            if parent is None:
                ProviderHierarchy.objects.create(
                    whose_id=user_id,
                    root=provider,
                )
