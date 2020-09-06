import csv

from operator import (
    methodcaller,
    itemgetter,
)

from django.contrib.auth.models import (
    User,
)
from django.core.management import (
    BaseCommand,
    CommandParser,
)
from django.db.transaction import (
    atomic,
)

from money.enums import (
    AccountActivityEnum,
)
from money.models import (
    Account,
    AccountHierarchy,
)


class Command(BaseCommand):
    help: str = (
        'Импортируемый csv-файл должен иметь '
        'кодировку utf-8, использовать точку с '
        'запятой в качестве разделителя и двойную '
        'кавычку в качестве ограничителя строк.\n\n'

        'Первая строка должна содержать заголовки '
        'столбцов "name", "parent" и "activity".\n\n'
        
        'Столбец "name" должен содержать уникальное '
        'имя счёта.\n\n'
        
        'Cтолбец "parent" должен содержать имя '
        'родительского счёта. Родительский счёт '
        'должен быть описан в файле раньше любого из '
        'его потомков.\n\n'

        'Столбец "activity" должен содержать одно из '
        'значений из money.enums.AccountActivityEnum. '
        'Значения последнего столбца значимы только '
        'для корневых счетов. Т.е. корень задаёт вид '
        'активности всего порождаемого им дерева '
        'счетов.\n\n'
        
        'Счёт считается корневым, если в столбце '
        '"parent" задана пустая строка.'
    )

    def add_arguments(self, parser: CommandParser):
        super().add_arguments(parser)
        parser.add_argument(
            'username',
        )
        parser.add_argument(
            'file_path',
        )

    @atomic
    def handle(self, username, file_path, *args, **options):
        user = User.objects.filter(username=username).get()

        source = open(file_path, 'rt', encoding='utf-8')
        items = csv.DictReader(source, delimiter=';')

        account_by_name = {}

        items_values = map(
            itemgetter(
                'name',
                'parent',
                'activity',
            ),
            items,
        )

        for name, parent_name, activity in items_values:

            if parent_name:
                try:
                    parent = account_by_name[parent_name]
                except KeyError:
                    raise ValueError(
                        'You have to define account "{parent}" before using it with account "{name}"'.format(  # noqa
                            parent=parent_name,
                            name=name,
                        ),
                    )
            else:
                parent = None

            account = Account.objects.create(
                parent=parent,
                name=name,
            )
            account_by_name[name] = account

            if parent is None:
                if activity not in AccountActivityEnum.values:
                    raise ValueError(
                        'There is no activity "{}"'.format(activity),
                    )

                AccountHierarchy.objects.create(
                    whose=user,
                    root=account,
                    activity=activity,
                )

        source.close()
