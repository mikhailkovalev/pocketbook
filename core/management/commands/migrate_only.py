from itertools import chain

from django.apps import apps
from django.core.management import (
    BaseCommand,
    call_command,
)
from django.db import connection


class Command(BaseCommand):
    help = (
        'После выполнения миграций удаляет все '
        'служебные данные из БД.'
    )

    tables_to_clear = (
        'auth_permission',
        'django_content_type',
        # 'django_migrations',
    )

    def __init__(self, stdout=None, stderr=None, no_color=False):
        super().__init__(stdout, stderr, no_color)
        self.tables_to_clear = list(self.tables_to_clear)

    def clear_tables(self):
        vendor = connection.vendor
        cursor = connection.cursor()

        if vendor == 'sqlite':
            self.tables_to_clear.extend((
                'sqlite_sequence',
            ))
        # Место для расширения таблиц под другие СУБД

        if vendor == 'sqlite':
            template = 'DELETE FROM {table_name};'
            for table in self.tables_to_clear:
                cursor.execute(
                    template.format(table_name=table))

        cursor.close()

    def handle(self, *args, **options):
        call_command('migrate')
        self.clear_tables()
