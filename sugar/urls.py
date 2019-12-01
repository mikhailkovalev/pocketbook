from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^records.json$',
        views.get_records,
        name='records',),
    url(
        r'^list.html$',
        views.list_view,
        name='list',
    ),
]
