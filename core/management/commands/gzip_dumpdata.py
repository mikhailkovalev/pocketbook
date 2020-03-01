import gzip
import json
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

    @staticmethod
    def get_data_model_version():
        version_conf_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            os.path.pardir,
            os.path.pardir,
            os.path.pardir,
            'version_conf.json',
        )
        version_conf_file = open(
            file=version_conf_path,
            mode='r',
            encoding='utf-8',
        )
        version_conf = json.load(version_conf_file)
        version_conf_file.close()
        return version_conf['data_model']['version']

    @classmethod
    def generate_filename(cls):
        data_model_version = cls.get_data_model_version()
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
        dumpdata = DumpDataCommand(stdout=output_stream)
        call_command(dumpdata, format='json')
        output_stream.close()
