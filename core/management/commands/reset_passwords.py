from typing import (
    TYPE_CHECKING,
    List,
)

from django.contrib.auth.models import User
from django.core.management import (
    BaseCommand,
)

if TYPE_CHECKING:
    from django.core.management import (
        CommandParser,
    )


class Command(BaseCommand):

    def add_arguments(self, parser: 'CommandParser'):
        parser.add_argument(
            'password',
        )
        parser.add_argument(
            'usernames',
            nargs='+',
        )

    def handle(self, password, usernames: List[str], *args, **options):
        users = User.objects.all()
        if usernames:
            users = users.filter(
                username__in=usernames,
            )

        for user in users:
            user.set_password(password)
            user.save()
