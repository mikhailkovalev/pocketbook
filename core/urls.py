from django.conf.urls import url

from . import views


urlpatterns = [
    url(
        r'dump',
        views.download_json_dump,
        name='download_json_dump',
    ),
]
