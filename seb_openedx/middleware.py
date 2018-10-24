""" Middleware for seb_openedx """

import sys
import inspect
from django.http import HttpResponseNotFound
from django.utils.deprecation import MiddlewareMixin
from django.utils.six.moves import filter as sixfilter  # pylint: disable=import-error
from django.conf import settings
from opaque_keys.edx.keys import CourseKey
from web_fragments.fragment import Fragment
from seb_openedx.edxapp_wrapper.edxmako_module import render_to_response, render_to_string
from seb_openedx.edxapp_wrapper.get_courseware_module import get_courseware_module
from seb_openedx.permissions import get_enabled_permission_classes
from seb_openedx.seb_courseware_index import SebCoursewareIndex
from seb_openedx.edxapp_wrapper.get_chapter_from_location import get_chapter_from_location

SEB_WHITELIST_PATHS = getattr(settings, 'SEB_WHITELIST_PATHS', [])
SEB_BLACKLIST_CHAPTERS = getattr(settings, 'SEB_BLACKLIST_CHAPTERS', [])


class SecureExamBrowserMiddleware(MiddlewareMixin):
    """ Middleware for seb_openedx """

    def process_view(self, request, view_func, view_args, view_kwargs):
        """ Start point of to d4etermine cms or lms """
        courseware = get_courseware_module()
        course_key_string = view_kwargs.get('course_key_string') or view_kwargs.get('course_id')
        course_key = CourseKey.from_string(course_key_string) if course_key_string else None
        access_denied = False

        if course_key:
            # By default is all denied
            access_denied = True

            if self.is_whitelisted_view(request, course_key):
                # First: Broad white-listing
                access_denied = False

            if self.is_blacklisted_chapter(request, course_key):
                # Second: Granular white-listing
                access_denied = True

            active_comps = get_enabled_permission_classes()
            for permission in active_comps:
                if permission().check(request, course_key):
                    access_denied = False

        if access_denied:
            is_courseware_view = bool(view_func.__name__ == courseware.views.index.CoursewareIndex.__name__)
            if is_courseware_view:
                return self.courseware_error_response(request, *view_args, **view_kwargs)
            return self.generic_error_response(request, course_key)
        return None

    def is_whitelisted_view(self, request, course_key):
        """ First broad filter: whitelisting of paths/tabs """

        # Whitelisting logic by alias
        aliases = {
            'discussion.views': 'discussion',
            'course_wiki.views': 'wiki',
            'openedx.features.course_experience': 'course-outline',
        }

        views_module = inspect.getmodule(request.resolver_match.func).__name__

        alias_current_path = next(sixfilter(lambda k: aliases[k] if views_module.startswith(k) else None, aliases), None)

        if alias_current_path in SEB_WHITELIST_PATHS:
            return True

        # Whitelisting xblocks when courseware
        if 'courseware' in SEB_WHITELIST_PATHS and self.is_xblock_request(request):
            return True

        # Whitelisting by url name
        if request.resolver_match.url_name:
            url_names_allowed = list(SEB_WHITELIST_PATHS) + ['jump_to', 'jump_to_id']
            for url_name in url_names_allowed:
                if request.resolver_match.url_name.startswith(url_name):
                    return True

        return False

    def is_blacklisted_chapter(self, request, course_key):
        """ Second more granular filter: blacklisting of specific chapters """
        chapter = request.resolver_match.kwargs.get('chapter')

        if not SEB_BLACKLIST_CHAPTERS:
            return False

        if chapter in SEB_BLACKLIST_CHAPTERS:
            return True

        if 'courseware' in SEB_WHITELIST_PATHS and self.is_xblock_request(request):
            usage_id = request.resolver_match.kwargs.get('usage_id')
            if usage_id:
                chapter = get_chapter_from_location(usage_id, course_key)
                if chapter in SEB_BLACKLIST_CHAPTERS:
                    return True
        return False

    def courseware_error_response(self, request, *view_args, **view_kwargs):
        """ error response when a chapter is being blocked """
        html = Fragment()
        html.add_content(render_to_string('seb-403-error-message.html', {}))
        SebCoursewareIndex.set_context_fragment(html)
        return SebCoursewareIndex.as_view()(request, *view_args, **view_kwargs)

    def generic_error_response(self, request, course_key):
        """ generic error response, full page 403 error (with course menu) """
        courseware = get_courseware_module()
        try:
            course = courseware.courses.get_course(course_key, depth=2)
        except ValueError:
            return HttpResponseNotFound()

        context = {
            'course': course,
            'request': request
        }

        return render_to_response('seb-403.html', context, status=403)

    def is_xblock_request(self, request):
        """ returns if it's an xblock HTTP request or not """
        return request.resolver_match.func.__name__ == 'handle_xblock_callback'

    @classmethod
    def is_installed(cls):
        """ Returns weather this middleware is installed in the running django instance """
        middleware_class_path = sys.modules[cls.__module__].__name__ + '.' + cls.__name__
        middlewares = settings.MIDDLEWARE_CLASSES if hasattr(settings, 'MIDDLEWARE_CLASSES') else settings.MIDDLEWARE
        return middleware_class_path in middlewares
