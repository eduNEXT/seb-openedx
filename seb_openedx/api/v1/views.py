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

from seb_openedx.api.v1.serializers import SebConfigurationSerializer
from seb_openedx.seb_keys_sources import get_config_by_course


LOG = logging.getLogger(__name__)


class SebConfiguration(APIView):
    """
    Handles all the CRUD operations on a Course SAFE_EXAM_BROWSER configuration
    """

    authentication_classes = (OAuth2Authentication, SessionAuthentication)
    permission_classes = (IsAdminUser,)
    renderer_classes = (JSONRenderer, BrowsableAPIRenderer)

    def get(self, request, course_id, *args, **kwargs):
        """
        Retrieves the current course configuration and validates it
        before returning it to the caller
        """
        course_key = CourseKey.from_string(course_id)
        config = get_config_by_course(course_key)
        serialized_config = SebConfigurationSerializer(data=config)
        serialized_config.is_valid(raise_exception=True)
        return Response(serialized_config.validated_data)
