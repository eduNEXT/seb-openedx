"""
Defines the entry point for all versions of the API
"""
from django.conf.urls import url, include


urlpatterns = [  # pylint: disable=invalid-name
    url(r'^v1/', include('seb_openedx.api.v1.urls', namespace='seb-api-v1')),
]
