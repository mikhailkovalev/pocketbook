import functools
import logging
import time

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from django.db.utils import OperationalError


logger = logging.getLogger(__name__)


class Command(BaseCommand):

    @staticmethod
    @functools.lru_cache(maxsize=None)
    def get_timeout():
        try:
            return settings.WAIT_DB_TIMEOUT
        except AttributeError:
            return 10

    def handle(self, *args, **kwargs):
        logger.info('Waiting for database become available...')
        start = time.perf_counter()
        while True:
            try:
                cursor = connection.cursor()
                cursor.execute('SELECT 1;')
                cursor.fetchone()[0]  # noqa
            except OperationalError as exc:
                duration = time.perf_counter() - start
                if duration > self.get_timeout():
                    logger.exception(str(exc), exc_info=exc)
                    raise CommandError(
                        f'Database unavailable after {duration:.3f} sec. {exc!r}',  # noqa
                        returncode=1,
                    )
            else:
                break

        logger.info('Database is available!')
