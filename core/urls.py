from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'',
        views.download_json_dump,
        name='download_json_dump'),
]
