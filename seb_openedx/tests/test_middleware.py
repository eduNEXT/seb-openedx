# -*- coding: utf-8 -*-
""" Tests for the main middleware class of the SEB Open edX plugin. """
import hashlib
import mock
from mock import Mock, patch
from django.test import RequestFactory, TestCase
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test.utils import override_settings
from seb_openedx.middleware import SecureExamBrowserMiddleware


@patch.object(SecureExamBrowserMiddleware, 'is_whitelisted_view', Mock(return_value=False))
@patch.object(SecureExamBrowserMiddleware, 'is_blacklisted_chapter', Mock(return_value=True))
@patch.object(SecureExamBrowserMiddleware, 'handle_masquerade', Mock(return_value=(None, None, {})))
@patch('seb_openedx.middleware.get_config_by_course', Mock(return_value={}))
@patch('seb_openedx.middleware.is_user_banned', Mock(return_value=False))
@patch('seb_openedx.middleware.ban_user', Mock(return_value=(False, False,)))
@override_settings(SEB_KEY_SOURCES=['from_other_course_settings'], SERVICE_VARIANT='lms')
class TestMiddleware(TestCase):
    """ Tests for the seb-open-edx page """
    def setUp(self):
        """ setup """
        super().setUp()
        course_key_pattern = r'(?P<course_key_string>[^/+]+(/|\+)[^/+]+(/|\+)[^/?]+)'
        self.url_pattern = f'^v1/courses/{course_key_pattern}'
        self.factory = RequestFactory()
        self.seb_middleware = SecureExamBrowserMiddleware(get_response=Mock())
        self.view = lambda course_key_string: None
        self.superuser = get_user_model().objects.create_superuser('test', 'test@example.com', 'test')
        self.course_params = {"course_key_string": "library-v1:TestX+lib1"}

    def create_fake_request(self):
        """ helper method to create a test request """
        request = self.factory.get(self.url_pattern)
        request.resolver_match = mock.MagicMock()
        request.user = mock.MagicMock()
        return request

    @mock.patch('seb_openedx.middleware.render_to_response')
    @override_settings(SEB_PERMISSION_COMPONENTS=[])
    def test_middleware_forbidden(self, m_render_to_string):
        """ Test that middleware returns forbidden when there is no class handling allowed requests """
        request = self.create_fake_request()
        self.seb_middleware.process_view(request, self.view, [], self.course_params)
        m_render_to_string.assert_called_once_with('seb-403.html', mock.ANY, status=403)

    @override_settings(SEB_PERMISSION_COMPONENTS=['AlwaysAllowStaff'])
    def test_middleware_is_staff(self):
        """ Test that middleware returns None if user is admin (is_staff) """
        request = self.create_fake_request()
        request.user = self.superuser
        response = self.seb_middleware.process_view(request, self.view, [], self.course_params)
        self.assertEqual(response, None)

    @mock.patch('seb_openedx.edxapp_wrapper.get_course_module.import_module', side_effect=lambda x: FakeModuleForSebkeysTesting())
    @override_settings(SEB_PERMISSION_COMPONENTS=['CheckSEBHashBrowserExamKey'])
    def test_middleware_sebkeys(self, m_import):
        """ Test that middleware returns None when valid seb key is given """
        request = self.create_fake_request()
        tohash = request.build_absolute_uri().encode() + FakeModuleForSebkeysTesting.other_course_settings['seb_keys'][0].encode()
        request.META['HTTP_X_SAFEEXAMBROWSER_REQUESTHASH'] = hashlib.sha256(tohash).hexdigest()
        response = self.seb_middleware.process_view(request, self.view, [], {"course_key_string": "library-v1:TestX+lib1"})
        self.assertEqual(response, None)
        m_import.assert_called_with(settings.SEB_COURSE_MODULE)


class FakeModuleForSebkeysTesting:
    """ Fake module for sebkeys middleware testing """
    other_course_settings = {"seb_keys": ["FAKE_SEB_KEY"]}

    def get_course_module(self, *args, **kwargs):
        """ needs to return an object with attribute other_course_settings, so just use itself """
        return self
