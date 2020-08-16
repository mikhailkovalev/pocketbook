from io import (
    StringIO,
)
from pprint import (
    pprint as pp,
)

from django.http import (
    HttpResponse,
)

from .helpers import (
    get_version_config,
)


def show_version(request):
    config = get_version_config()

    stream = StringIO()
    pp(
        object=config,
        stream=stream,
        indent=4,
    )

    value = stream.getvalue().replace('\n', '<br>')

    return HttpResponse(value)
