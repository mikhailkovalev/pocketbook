import gzip
import json
from datetime import datetime

from django.core.management import (
    BaseCommand,
    call_command,
)
from django.core.management.commands.dumpdata import (
    Command as DumpDataCommand,
)

from core.datetime_helpers import (
    with_server_timezone,
)


class Command(BaseCommand):
    help = (
        'Создаёт сжатый файл данных в заданном '
        'формате, с указанием версии модели '
        'данных.'
    )

    @staticmethod
    def get_data_model_version():
        version_conf_path = 'version_conf.json'
        version_conf_file = open(version_conf_path, 'r', encoding='utf-8')
        version_conf = json.load(version_conf_file)
        return version_conf['data_model']['version']

    def handle(self, *args, **options):
        data_model_version = self.get_data_model_version()
        today_verbose = with_server_timezone(
            datetime.now(),
        ).strftime(
            '%Y-%m-%d',
        )
        output_filename = '{prefix}-{date}-v{version}.json.gz'.format(
            prefix='pocketbook',
            date=today_verbose,
            version=data_model_version,
        )
        output_stream = gzip.open(output_filename, 'wt')
        dumpdata = DumpDataCommand(stdout=output_stream)
        call_command(dumpdata, format='json')
        output_stream.close()
