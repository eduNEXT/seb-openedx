"""
API v1 views.
"""
from __future__ import absolute_import, unicode_literals
import logging

from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAdminUser
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_oauth.authentication import OAuth2Authentication

from opaque_keys.edx.keys import CourseKey

LOG = logging.getLogger(__name__)


class SebConfiguration(APIView):
    """
    Handles API requests to create users
    """

    authentication_classes = (OAuth2Authentication, SessionAuthentication)
    permission_classes = (IsAdminUser,)
    renderer_classes = (JSONRenderer, BrowsableAPIRenderer)

    def get(self, request, course_id, *args, **kwargs):
        """
        """
        course_key = CourseKey.from_string(course_id)
        return Response({"raw_data": unicode(course_key)})