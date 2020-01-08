import os.path

from operator import (
    attrgetter,
)

from django.contrib.auth.decorators import (
    user_passes_test,
)
from django.core.management import (
    call_command,
)
from django.http import (
    Http404,
    HttpResponse,
)

from core.management.commands.gzip_dumpdata import (
    Command as GzipDumpDataCommand,
)


@user_passes_test(
    test_func=attrgetter('is_superuser'),

    # FIXME: избавиться от хардкода
    login_url='/admin/login',
)
def download_json_dump(request):
    cmd = GzipDumpDataCommand()
    filename = GzipDumpDataCommand.generate_filename()

    call_command(cmd, filename=filename)
    filepath = GzipDumpDataCommand.get_filepath(filename)

    if os.path.exists(filepath):
        with open(filepath, 'rb') as dump_file:
            response = HttpResponse(
                content=dump_file.read(),
                content_type='application/gzip',
            )
            response['Content-Disposition'] = (
                f'inline; filename={filename}')
            return response
    raise Http404
