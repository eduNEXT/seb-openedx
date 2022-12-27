# -*- coding: utf-8 -*-
""" Tests for the api views of the SEB Open edX plugin. """
from mock import Mock, patch, ANY
from django.test import TestCase
from django.contrib.auth.models import User

from rest_framework.test import APIClient


class TestServerAPI(TestCase):
    """ Tests for the seb-open-edx page """
    def setUp(self):
        """ setup """
        super().setUp()
        self.api_user = User('test', 'test@example.com', 'test', is_staff=True)
        self.client = APIClient()
        self.client.force_authenticate(user=self.api_user)

    @patch(
        'seb_openedx.api.v1.views.get_config_by_course',
        Mock(return_value={"BROWSER_KEYS": ["original"]})
    )
    def test_api_get(self):
        """ Test that the GET method works under normal conditions """
        course_id = 'course-v1:seb+course+run'
        response = self.client.get(f'/api/v1/course/{course_id}/configuration/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('BROWSER_KEYS')[0], 'original')

    @patch('seb_openedx.api.v1.views.get_config_by_course', Mock(return_value={}))
    def test_api_get_not_found(self):
        """ Test that GET on an unexistant course returns 404 """
        course_id = 'course-v1:seb+course+run'
        response = self.client.get(f'/api/v1/course/{course_id}/configuration/')
        self.assertEqual(response.status_code, 404)

    @patch('seb_openedx.api.v1.views.get_config_by_course', Mock(return_value={}))
    @patch('seb_openedx.api.v1.views.save_course_config')
    def test_api_post(self, m_save_course_config):
        """ Test that POST works under normal conditions """
        course_id = 'course-v1:seb+course+run'
        response = self.client.post(f'/api/v1/course/{course_id}/configuration/', {})

        m_save_course_config.assert_called_once()
        self.assertEqual(response.status_code, 200)

    @patch('seb_openedx.api.v1.views.get_config_by_course', Mock(return_value={"BROWSER_KEYS": ["original"]}))
    @patch('seb_openedx.api.v1.views.save_course_config')
    def test_api_post_found(self, m_save_course_config):
        """ Test POSTing to an existing key fails """
        course_id = 'course-v1:seb+course+run'
        response = self.client.post(f'/api/v1/course/{course_id}/configuration/', {})

        m_save_course_config.assert_not_called()
        self.assertEqual(response.status_code, 422)

    @patch('seb_openedx.api.v1.views.get_config_by_course', Mock(return_value={"BROWSER_KEYS": ["original"]}))
    @patch('seb_openedx.api.v1.views.save_course_config')
    def test_api_put(self, m_save_course_config):
        """ Test that PUT works on normal conditions """
        course_id = 'course-v1:seb+course+run'
        payload = {'BROWSER_KEYS': ['updated']}
        response = self.client.put(f'/api/v1/course/{course_id}/configuration/', payload)

        m_save_course_config.assert_called_once()
        self.assertEqual(m_save_course_config.call_args[0][1]['BROWSER_KEYS'], ['updated'])
        self.assertEqual(response.status_code, 200)

    @patch('seb_openedx.api.v1.views.get_config_by_course')
    @patch('seb_openedx.api.v1.views.save_course_config')
    def test_api_patch(self, m_save_course_config, m_get_config_by_course):
        """ Test that PATCH works on normal conditions """
        course_id = 'course-v1:seb+course+run'
        m_get_config_by_course.return_value = {"BROWSER_KEYS": ["original"]}

        response = self.client.patch(f'/api/v1/course/{course_id}/configuration/', {"CONFIG_KEYS": ["updated"]})

        m_save_course_config.assert_called_once()
        m_get_config_by_course.assert_called_once()
        self.assertEqual(response.status_code, 200)

    @patch('seb_openedx.api.v1.views.get_config_by_course')
    @patch('seb_openedx.api.v1.views.save_course_config')
    def test_api_delete(self, m_save_course_config, m_get_config_by_course):
        """ Test that DELETE works on normal conditions """
        course_id = 'course-v1:seb+course+run'
        m_get_config_by_course.return_value = {}

        response = self.client.delete(f'/api/v1/course/{course_id}/configuration/')

        m_save_course_config.assert_called_once_with(ANY, None, user_id=ANY)
        m_get_config_by_course.assert_called_once()
        self.assertEqual(response.status_code, 204)
