""" Middleware for seb_openedx """

from __future__ import absolute_import, unicode_literals, print_function
import sys
import inspect
import logging

from django.http import HttpResponseNotFound
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from opaque_keys.edx.keys import CourseKey
from web_fragments.fragment import Fragment
from seb_openedx.edxapp_wrapper.edxmako_module import render_to_string, render_to_response
from seb_openedx.edxapp_wrapper.get_courseware_module import get_courseware_module
from seb_openedx.edxapp_wrapper.get_courseware_index_view import get_courseware_index_view
from seb_openedx.lazy_import_seb_courseware_index import LazyImportSebCoursewareIndex
from seb_openedx.edxapp_wrapper.get_chapter_from_location import get_chapter_from_location
from seb_openedx.user_banning import is_user_banned, ban_user
from seb_openedx.permissions import get_enabled_permission_classes
from seb_openedx.seb_keys_sources import get_config_by_course

LOG = logging.getLogger(__name__)

COURSE_METADATA_PATH = 'lms.djangoapps.course_home_api.course_metadata.views'


class SecureExamBrowserMiddleware(MiddlewareMixin):
    """ Middleware for seb_openedx """

    # pylint: disable=too-many-locals
    def process_view(self, request, view_func, view_args, view_kwargs):
        """ Start point """

        if settings.SERVICE_VARIANT == 'cms':
            return None

        course_key_string = view_kwargs.get('course_key_string') or view_kwargs.get('course_id')
        course_key = CourseKey.from_string(course_key_string) if course_key_string else None

        # When the request is for masquerade (ajax) we leave it alone
        if self.get_view_path(request) == 'courseware.masquerade':
            return None

        # Whitelist API endpoints except course_metadata
        if request.path.startswith('/api/') and self.get_view_path(request) != COURSE_METADATA_PATH:
            return None

        if course_key:
            # By default is all denied
            access_denied = True

            config = get_config_by_course(course_key)

            if self.is_whitelisted_view(config, request, course_key):
                # First: Broad white-listing
                access_denied = False

            if self.is_blacklisted_chapter(config, request, course_key):
                # Second: Granular black-listing
                access_denied = True

            user_name, masquerade, context = self.handle_masquerade(request, course_key)

            if not masquerade:
                user_name = request.user.username

            banned = is_user_banned(user_name, course_key)

            if not banned:
                for permission in get_enabled_permission_classes(course_key):
                    if permission().check(request, course_key, masquerade):
                        access_denied = False
                    else:
                        LOG.info("Permission: %s denied for: %s.", permission, user_name)

            if access_denied:
                return self.handle_access_denied(
                    request,
                    view_func,
                    view_args,
                    view_kwargs,
                    course_key,
                    context,
                    user_name
                )

        return None

    def supports_preview_menu(self, request):
        """ check if current view support preview_menu or not """
        return bool(request.resolver_match.func.__name__ == get_courseware_index_view().__name__)\
            or inspect.getmodule(request.resolver_match.func).__name__.startswith('openedx.features.course_experience')

    def handle_masquerade(self, request, course_key):
        """ masquerade """
        courseware = get_courseware_module()
        masquerade = request.session.get('masquerade_settings', {}).get(course_key)
        user_name = getattr(masquerade, 'user_name', None)

        if masquerade:
            context = {
                'course': courseware.courses.get_course(course_key),
                'supports_preview_menu': self.supports_preview_menu(request),
                'staff_access': request.user.is_staff,
                'masquerade': masquerade,
            }
            return user_name, masquerade, context
        return None, None, {}

    # pylint: disable=too-many-arguments
    def handle_access_denied(self, request, view_func, view_args, view_kwargs, course_key, context, user_name):
        """ handle what to return and do when access denied """
        if self.get_view_path(request) == COURSE_METADATA_PATH:
            response = view_func(request, *view_args, **view_kwargs)
            response.data.update({
                "course_access": {
                    "has_access": False,
                    "error_code": "audit_expired",
                    "additional_context_user_message": "Please use Safe Exam Browser to access this course."
                }
            })
            return response
        is_banned, new_ban = ban_user(user_name, course_key, request.user.username)
        is_courseware_view = bool(view_func.__name__ == get_courseware_index_view().__name__)
        context.update({"banned": is_banned, "is_new_ban": new_ban})
        if is_courseware_view:
            return self.courseware_error_response(request, context, *view_args, **view_kwargs)
        return self.generic_error_response(request, course_key, context)

    def is_whitelisted_view(self, config, request, course_key):
        """ First broad filter: whitelisting of paths/tabs """

        # Whitelisting logic by alias
        aliases = {
            'discussion.views': 'discussion',
            'course_wiki.views': 'wiki',
            'openedx.features.course_experience': 'course-outline',
        }

        views_module = inspect.getmodule(request.resolver_match.func).__name__
        paths_matched = [value for key, value in aliases.items() if views_module.startswith(key)]
        alias_current_path = paths_matched[0] if paths_matched else None
        whitelist_paths = config.get('WHITELIST_PATHS', [])

        if views_module.startswith('seb_openedx.api'):
            return True

        if not whitelist_paths:
            return False

        if alias_current_path in whitelist_paths:
            return True

        # Whitelisting xblocks when courseware
        if 'courseware' in whitelist_paths and self.is_xblock_request(request):
            return True

        # Whitelisting by url name
        if request.resolver_match.url_name:
            url_names_allowed = list(whitelist_paths) + ['jump_to', 'jump_to_id']
            for url_name in url_names_allowed:
                if request.resolver_match.url_name.startswith(url_name):
                    return True

        return False

    def is_blacklisted_chapter(self, config, request, course_key):
        """ Second more granular filter: blacklisting of specific chapters """
        chapter = request.resolver_match.kwargs.get('chapter')
        blackist_chapters = config.get('BLACKLIST_CHAPTERS', [])

        if not blackist_chapters:
            return False

        if chapter in blackist_chapters:
            return True

        if 'courseware' in config.get('WHITELIST_PATHS', []) and self.is_xblock_request(request):
            usage_id = request.resolver_match.kwargs.get('usage_id')
            if usage_id:
                chapter = get_chapter_from_location(usage_id, course_key)
                if chapter in blackist_chapters:
                    return True
        return False

    def courseware_error_response(self, request, context, *view_args, **view_kwargs):
        """ error response when a chapter is being blocked """
        html = Fragment()
        html.add_content(render_to_string('seb-403-error-message.html', context))
        SebCoursewareIndex = LazyImportSebCoursewareIndex.get_or_create_class()  # pylint: disable=invalid-name
        SebCoursewareIndex.set_context_fragment(html)
        return SebCoursewareIndex.as_view()(request, *view_args, **view_kwargs)

    def generic_error_response(self, request, course_key, context):
        """ generic error response, full page 403 error (with course menu) """
        courseware = get_courseware_module()
        try:
            course = courseware.courses.get_course(course_key, depth=2)
        except ValueError:
            return HttpResponseNotFound()

        context.update({
            'course': course,
            'request': request
        })

        return render_to_response('seb-403.html', context, status=403)

    def is_xblock_request(self, request):
        """ returns if it's an xblock HTTP request or not """
        return request.resolver_match.func.__name__ == 'handle_xblock_callback'

    def get_view_path(self, request):
        """ get full import path of match resolver """
        return inspect.getmodule(request.resolver_match.func).__name__

    @classmethod
    def is_installed(cls):
        """ Returns weather this middleware is installed in the running django instance """
        middleware_class_path = sys.modules[cls.__module__].__name__ + '.' + cls.__name__
        middlewares = settings.MIDDLEWARE_CLASSES if hasattr(settings, 'MIDDLEWARE_CLASSES') else settings.MIDDLEWARE
        return middleware_class_path in middlewares
