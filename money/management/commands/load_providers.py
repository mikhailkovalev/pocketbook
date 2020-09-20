from typing import (
    Iterator,
    NamedTuple,
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

