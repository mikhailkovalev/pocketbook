from django.contrib.contenttypes.models import (
    ContentType,
)
from django.core.management import (
    BaseCommand,
    CommandParser,
    call_command,
)
from django.core.management.commands.migrate import (
    Command as MigrateCommand,
)
from django.core.management.commands.loaddata import (
    Command as LoadDataCommand,
)


class Command(BaseCommand):
    help: str = (
        'Равносильно последовательному выполнению '
        'команд `migrate` и `loaddata`.'
    )

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.stdout.ending = ''
        self.stderr.ending = ''

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            'path_to_data',
        )

    def handle(self, path_to_data: str, **kw) -> None:
        self._do_migrate()
        self._clean_contenttypes()
        self._do_load_data(path_to_data)

    def _do_migrate(self) -> None:
        migrate_command = MigrateCommand(
            stdout=self.stdout,
            stderr=self.stderr,
        )
        call_command(
            migrate_command,
        )

    @staticmethod
    def _clean_contenttypes() -> None:
        ContentType.objects.all().delete()

    def _do_load_data(self, path_to_data: str) -> None:
        load_data_command = LoadDataCommand(
            stdout=self.stdout,
            stderr=self.stderr,
        )
        call_command(
            load_data_command,
            path_to_data,
        )
