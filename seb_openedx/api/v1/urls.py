"""
This file defines a the actual urls for the version 1 of the api
"""
from django.conf import settings
from django.conf.urls import url
from seb_openedx.api.v1 import views

app_name = 'seb-api-v1'  # pylint: disable=invalid-name

urlpatterns = [  # pylint: disable=invalid-name
    url(
        f'course/{settings.COURSE_ID_PATTERN}/configuration/',
        views.SebConfiguration.as_view(),
        name='seb-configuration-api'
    ),
]
