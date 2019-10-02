from django.conf.urls import url

from . import views


urlpatterns = [
    url(
        r'^records.json$',
        views.get_records,
        name='records',
    ),
]
