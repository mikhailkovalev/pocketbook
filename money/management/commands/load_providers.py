from django.core.management import (
    BaseCommand,
    CommandParser,
)


class Command(BaseCommand):

    def add_arguments(self, parser: CommandParser):
        pass

    def handle(self, *args, **options):
        pass
