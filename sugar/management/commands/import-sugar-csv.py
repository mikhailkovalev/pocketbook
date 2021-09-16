import csv
import pytz
import re
from argparse import (
    RawTextHelpFormatter,
)
from datetime import (
    datetime,
)
from decimal import (
    Decimal,
    DecimalException,
)
from itertools import (
    chain,
)
from operator import (
    itemgetter,
)
from typing import (
    Any,
    Dict,
    List,
    Pattern,
)

from django.apps import (
    apps,
)
from django.conf import (
    settings,
)
from django.core.management.base import (
    BaseCommand,
    CommandParser,
)

from sugar.models import (
    Record,
    SugarMetering,
    TestStripPack,
)


User = apps.get_model(settings.AUTH_USER_MODEL)  # noqa


class Command(BaseCommand):
    ENCODING: str = 'utf-8'
    QUOTE: str = '"'
    DELIMITER: str = ';'

    DATE_PATTERN: Pattern = re.compile(r'^(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})$')  # noqa
    TIME_PATTERN: Pattern = re.compile(r'^(?P<hour>\d\d?):(?P<minute>\d\d?)$')
    SUGAR_LEVEL_PATTERN: Pattern = re.compile(r'^\d\d?(\.\d)?$')

    @property
    def help(self) -> str:
        return (
            f'Expected encoding: {self.ENCODING}\n'
            f'Expected QUOTE: {self.QUOTE}\n'
            f'Expected DELIMITER: {self.DELIMITER}\n'
            f'Expected columns:\n'
            f'    Date: %Y-%m-%d\n'
            f'    Time: %H:%M\n'
            f'    SugarLevel: decimal(3, 1)\n'
        )

    def create_parser(self, prog_name, subcommand) -> CommandParser:
        parser = super().create_parser(prog_name, subcommand)
        parser.formatter_class = RawTextHelpFormatter
        return parser

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            '-u',
            '--user',
            dest='username',
            required=True,
            type=str,
        )
        parser.add_argument(
            '-f',
            '--file',
            dest='csv_file_path',
            required=True,
            type=str,
            help='Path to csv-file'
        )

    @staticmethod
    def get_user(username: str) -> User:
        try:
            return User.objects.filter(username=username).get()
        except User.DoesNotExist:
            raise ValueError(f'There is no user {username!r}')

    @staticmethod
    def get_pack(user: User) -> TestStripPack:
        try:
            pack = TestStripPack.objects.filter(
                whose=user,
                expiry_actual__isnull=True,
            ).get()
        except TestStripPack.DoesNotExist:
            raise ValueError(
                'There is no "TestStripPack" object which is not expired!',
            )
        except TestStripPack.MultipleObjectsReturned:
            raise ValueError(
                'There are many "TestStripPack" objects which are not expired!',
            )

        return pack

    def handle(self, username, csv_file_path: str, *args, **kwargs) -> None:
        timezone = pytz.timezone(settings.TIME_ZONE)

        user = self.get_user(username)
        pack = self.get_pack(user)

        records_data: Dict[datetime, Dict[str, Any]] = {}
        records: List[Record] = []

        with open(csv_file_path, 'rt', encoding=self.ENCODING) as csv_file:
            reader = csv.reader(
                csv_file,
                delimiter=self.DELIMITER,
                quotechar=self.QUOTE,
            )

            for row_idx, row in enumerate(reader):
                date_match = self.DATE_PATTERN.match(row[0])
                time_match = self.TIME_PATTERN.match(row[1])

                if date_match is None:
                    raise ValueError(
                        f'Incorrect date value {row[0]!r} in line {row_idx+1}',
                    )

                if time_match is None:
                    raise ValueError(
                        f'Incorrect time value {row[1]!r} in line {row_idx+1}',
                    )

                when = timezone.localize(datetime(
                    year=int(date_match.group('year')),
                    month=int(date_match.group('month')),
                    day=int(date_match.group('day')),
                    hour=int(time_match.group('hour')),
                    minute=int(time_match.group('minute')),
                ))

                records.append(Record(
                    who=user,
                    when=when,
                ))

                sugar_level_match = self.SUGAR_LEVEL_PATTERN.match(row[2])
                if sugar_level_match is None:
                    raise ValueError(
                        f'Incorrect sugar_level value {row[2]!r} in line {row_idx+1}',
                    )

                records_data[when] = {
                    'sugar_metering': SugarMetering(
                        sugar_level=Decimal(row[2]),
                        pack=pack,
                    ),
                }

        Record.objects.bulk_create(records)

        created_records_by_when: Dict[datetime, Any] = dict(
            Record.objects.filter(
                when__in=tuple(map(
                    datetime.isoformat,
                    records_data.keys(),  # noqa
                )),
            ).values_list(
                'when',
                'pk',
            ),
        )

        for when, data in records_data.items():
            data['sugar_metering'].record_id = created_records_by_when[when]

        SugarMetering.objects.bulk_create(map(
            itemgetter('sugar_metering'),
            records_data.values(),
        ))
