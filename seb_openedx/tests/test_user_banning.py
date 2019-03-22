# -*- coding: utf-8 -*-
""" Tests for the main user banning feature of the SEB Open edX plugin. """
from mock import Mock, patch

from django.test import RequestFactory, TestCase
from django.contrib.auth import get_user_model
from django.test.utils import override_settings

from seb_openedx.middleware import SecureExamBrowserMiddleware


@patch.object(SecureExamBrowserMiddleware, 'handle_masquerade', Mock(return_value=(None, None, {})))
@override_settings(SEB_KEY_SOURCES=['from_other_course_settings'], SERVICE_VARIANT='lms', SEB_USER_BANNING_ENABLED=True)
class TestUserBanning(TestCase):
    """ Tests for the feature that bans a user definitively """
    def setUp(self):
        """ Setup """
        course_key_pattern = r'(?P<course_key_string>[^/+]+(/|\+)[^/+]+(/|\+)[^/?]+)'
        self.url_pattern = r'^v1/courses/{}'.format(course_key_pattern)
        self.seb_middleware = SecureExamBrowserMiddleware()
        self.factory = RequestFactory()
        self.view = lambda course_key_string: None
        self.course_params = {"course_key_string": "course-v1:SebX+ID+run"}
        self.user = get_user_model().objects.create_user(username='user_ban', password='password')

    def tearDown(self):
        """ Delete artifacts """
        self.user.delete()

    def create_fake_request(self):
        """ helper method to create a test request """
        request = self.factory.get(self.url_pattern)
        request.resolver_match = Mock()
        request.user = self.user
        return request

    @patch.object(SecureExamBrowserMiddleware, 'handle_access_denied')
    @patch('seb_openedx.middleware.get_config_by_course', Mock(return_value={}))
    @patch('seb_openedx.user_banning.get_config_by_course', Mock(return_value={}))
    @override_settings(SEB_PERMISSION_COMPONENTS=['AlwaysDenyAccess'])
    def test_user_blocking_works_deny(self, mock_access_denied):
        """ Testing a user is denied access by the middleware the first time """
        request = self.create_fake_request()

        self.seb_middleware.process_view(request, self.view, [], self.course_params)

        mock_access_denied.assert_called_once()

    @patch.object(SecureExamBrowserMiddleware, 'handle_access_denied')
    @patch('seb_openedx.middleware.get_config_by_course', Mock(return_value={}))
    @patch('seb_openedx.user_banning.get_config_by_course', Mock(return_value={}))
    @override_settings(SEB_PERMISSION_COMPONENTS=['AlwaysGrantAccess'])
    def test_user_blocking_works_grant(self, mock_access_denied):
        """ Testing a user is granted access by the middleware the first time """
        request = self.create_fake_request()

        response = self.seb_middleware.process_view(request, self.view, [], self.course_params)

        mock_access_denied.assert_not_called()
        self.assertEqual(response, None)

    @patch.object(SecureExamBrowserMiddleware, 'generic_error_response')
    @patch('seb_openedx.middleware.get_config_by_course', Mock(return_value={}))
    @patch('seb_openedx.user_banning.get_config_by_course', Mock(return_value={}))
    def test_user_banning_works(self, mock_response):
        """ Testing a user is denied access by the middleware the first time and subsecuent times with an older ban """
        request = self.create_fake_request()
        # first time

        with override_settings(SEB_PERMISSION_COMPONENTS=['AlwaysDenyAccess']):
            self.seb_middleware.process_view(request, self.view, [], self.course_params)
            mock_response.assert_called_once()
            _, _, context = mock_response.call_args[0]
            self.assertTrue(context.get('banned'))
            self.assertTrue(context.get('is_new_ban'))

        # clean mock
        mock_response.reset_mock()

        with override_settings(SEB_PERMISSION_COMPONENTS=['AlwaysGrantAccess']):
            # second time
            self.seb_middleware.process_view(request, self.view, [], self.course_params)
            mock_response.assert_called_once()
            _, _, context = mock_response.call_args[0]
            self.assertFalse(context.get('is_new_ban'))
            self.assertTrue(context.get('banned'))
