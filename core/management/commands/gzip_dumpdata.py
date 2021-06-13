import gzip
import os.path

from datetime import datetime

from django.conf import (
    settings,
)
from django.core.management import (
    BaseCommand,
    call_command,
)
from django.core.management.commands.dumpdata import (
    Command as DumpDataCommand,
)

from core.helpers import (
    with_server_timezone,
)

from main.helpers import (
    get_data_model_version,
)


class Command(BaseCommand):
    help = (
        'Создаёт сжатый файл данных в заданном '
        'формате, с указанием версии модели '
        'данных.'
    )

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            '--file',
            default=None,
            dest='filename',
            help='Имя файла, в который производить сохранение',
        )

    @classmethod
    def generate_filename(cls):
        data_model_version = get_data_model_version()
        today_verbose = with_server_timezone(
            datetime.now(),
        ).strftime(
            '%Y-%m-%d_%H-%M-%S',
        )
        filename = '{prefix}-{date}-v{version}.json.gz'.format(
            prefix='pocketbook',
            date=today_verbose,
            version=data_model_version,
        )
        return filename

    @staticmethod
    def get_filepath(filename):
        return os.path.join(
            settings.MEDIA_ROOT,
            filename,
        )

    def handle(self, filename, *args, **options):
        if filename is None:
            filename = self.generate_filename()

        output_filepath = self.get_filepath(filename)
        output_stream = gzip.open(output_filepath, 'wt')
        dumpdata = DumpDataCommand(
            stdout=output_stream,
        )
        call_command(
            command_name=dumpdata,
            format='json',
        )
        output_stream.close()
