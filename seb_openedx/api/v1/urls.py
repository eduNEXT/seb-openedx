"""
This file defines a the actual urls for the version 1 of the api
"""
from django.conf import settings
from django.conf.urls import url
from seb_openedx.api.v1 import views

app_name = 'seb-api-v1'

urlpatterns = [  # pylint: disable=invalid-name
    url(
        r'^course/{}/configuration/$'.format(settings.COURSE_ID_PATTERN),
        views.SebConfiguration.as_view(),
        name='seb-configuration-api'
    ),
]
