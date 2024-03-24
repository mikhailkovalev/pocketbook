import pathlib
from decimal import Decimal

import pytest
from django.db.utils import (
    IntegrityError,
)

from sugar import models


@pytest.mark.parametrize('db_data_base_dir', [pathlib.Path('sugar', 'db_data', 'test_models')])
@pytest.mark.parametrize('db_data_filename', ['test_multiple_meterings_basic.yml'])
def test_multiple_meterings(db_data):
    record = models.Record.objects.get()
    pack = models.TestStripPack.objects.get()

    with pytest.raises(IntegrityError):
        models.SugarMetering.objects.create(
            record=record,
            pack=pack,
            sugar_level=Decimal('6.0')
        )
