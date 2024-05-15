""" Middleware for seb_openedx """

from __future__ import absolute_import, unicode_literals, print_function
import sys
import inspect
import logging
import re

from django.http import HttpResponseNotFound
from django.conf import settings
from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import CourseKey, UsageKey
from web_fragments.fragment import Fragment
from seb_openedx.edxapp_wrapper.edxmako_module import render_to_string, render_to_response
from seb_openedx.edxapp_wrapper.get_courseware_module import get_courseware_module
from seb_openedx.edxapp_wrapper.get_courseware_index_view import get_courseware_index_view
from seb_openedx.lazy_import_seb_courseware_index import LazyImportSebCoursewareIndex
from seb_openedx.edxapp_wrapper.get_chapter_from_location import get_chapter_from_location
from seb_openedx.edxapp_wrapper.get_parent_from_location import get_parent_from_location
from seb_openedx.user_banning import is_user_banned, ban_user
from seb_openedx.permissions import get_enabled_permission_classes
from seb_openedx.seb_keys_sources import get_config_by_course

LOG = logging.getLogger(__name__)


class SecureExamBrowserMiddleware:
    """ Middleware for seb_openedx """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        """ Base method of the clase based middleware """
        response = self.get_response(request)
        return response

    # pylint: disable=too-many-locals,too-many-return-statements,too-many-branches
    def process_view(self, request, view_func, view_args, view_kwargs):
        """ Start point """

        if settings.SERVICE_VARIANT == 'cms':
            return None

        course_key_string = view_kwargs.get('course_key_string') or view_kwargs.get('course_id')
        try:
            course_key = CourseKey.from_string(course_key_string) if course_key_string else None
        except InvalidKeyError:
            course_key = None

        if course_key is None:
            usage_key_string = view_kwargs.get('usage_key_string')
            usage_key = UsageKey.from_string(usage_key_string) if usage_key_string else None
            course_key = usage_key.course_key if usage_key else None
        # When the request is for masquerade (ajax) we leave it alone
        if any([
            self.get_view_path(request) == 'courseware.masquerade',
            re.match(f'^/courses/{settings.COURSE_KEY_REGEX}/masquerade', request.path),
        ]):
            return None

        if course_key:
            # By default is all denied
            access_denied = True

            config = get_config_by_course(course_key)

            if settings.SEB_INDIVIDUAL_COURSE_ACTIVATION and not config.get("ENABLED", False):
                return None

            if self.is_whitelisted_view(config, request, course_key):
                # First: Broad white-listing
                access_denied = False

            if self.is_blacklisted_chapter(config, request, course_key):
                # Second: Granular black-listing
                access_denied = True

            if self.is_blacklisted_sequence(config, request, course_key):
                # Third: Granular subsection level black-listing
                access_denied = True

            if self.is_blacklisted_vertical(config, request, course_key):
                # Fourth: Granular unit level black-listing
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
                        LOG.info("Permission: %s denied for: %s. | %s", permission, user_name, request.path)

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
        is_banned, new_ban = ban_user(user_name, course_key, request.user.username)
        is_courseware_view = bool(view_func.__name__ == get_courseware_index_view().__name__)
        context.update({"banned": is_banned, "is_new_ban": new_ban})
        if is_courseware_view:
            return self.courseware_error_response(request, context, *view_args, **view_kwargs)

        is_xblock_view = bool(view_func.__name__ == 'render_xblock')
        if is_xblock_view:
            return self.xblock_error_response(request, context, *view_args, **view_kwargs)

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

        # MFEs require more granular blocks than module level
        allow_mfes = config.get('ALLOW_MFE_ACCESS', settings.SEB_ALLOW_MFE_ACCESS)
        if allow_mfes and any([
            # urls to allow whitelisting the block
            re.match(f'^/api/courseware/course/{settings.COURSE_KEY_REGEX}.*', request.path),
            re.match(f'^/api/courseware/sequence/{settings.USAGE_ID_PATTERN}.*', request.path),

            # this call returns the tree of block units
            re.match(f'^/api/course_home/outline/{settings.COURSE_KEY_REGEX}.*', request.path),

            # jump_to allows deeplinking
            re.match(f'^/courses/{settings.COURSE_KEY_REGEX}/jump_to/.*', request.path),

            # other APIs called by the learning MFE that contain no content
            re.match(f'^/api/course_home/course_metadata/{settings.COURSE_KEY_REGEX}.*', request.path),
            re.match(f'^/courses/{settings.COURSE_KEY_REGEX}/courseware-search/enabled/.*', request.path),
            re.match(f'^/api/edx_proctoring/v1/proctored_exam/attempt/course_id/{settings.COURSE_KEY_REGEX}.*', request.path),
        ]):
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
        blacklist_chapters = config.get('BLACKLIST_CHAPTERS', [])

        if not blacklist_chapters:
            return False

        if chapter in blacklist_chapters:
            return True

        if 'courseware' in config.get('WHITELIST_PATHS', []) and self.is_xblock_request(request):
            usage_id = request.resolver_match.kwargs.get('usage_id')
            usage_key_string = request.resolver_match.kwargs.get('usage_key_string')

            if usage_id:
                chapter = get_chapter_from_location(usage_id, course_key)
            elif usage_key_string:
                chapter = get_chapter_from_location(usage_key_string, course_key)

            if chapter in blacklist_chapters:
                return True
        return False

    def is_blacklisted_sequence(self, config, request, course_key):
        """ Third more granular filter: blacklisting of specific subsections (sequence | exam) """
        blacklist_sequences = config.get('BLACKLIST_SEQUENCES', [])
        if not blacklist_sequences:
            return False

        if self.is_xblock_request(request):
            usage_key_string = request.resolver_match.kwargs.get('usage_key_string')
            sequence = get_parent_from_location(usage_key_string, course_key, level='sequence')
            if sequence in blacklist_sequences:
                return True

        return False

    def is_blacklisted_vertical(self, config, request, course_key):
        """ Third more granular filter: blacklisting of specific units (verticals) """
        blacklist_verticals = config.get('BLACKLIST_VERTICALS', [])
        if not blacklist_verticals:
            return False

        if self.is_xblock_request(request):
            usage_key_string = request.resolver_match.kwargs.get('usage_key_string')
            vertical = get_parent_from_location(usage_key_string, course_key, level='vertical')
            if vertical in blacklist_verticals:
                return True

        return False

    def xblock_error_response(self, request, context, *view_args, **view_kwargs):
        """ error response when a chapter is being blocked in the MFE """
        context.update({
            'disable_accordion': True,
            'allow_iframing': True,
            'disable_header': True,
            'disable_footer': True,
            'disable_window_wrap': True,
            'on_courseware_page': True,
            'render_course_wide_assets': True,
        })
        response = render_to_response('seb-xblock.html', context, status=200)
        response.xframe_options_exempt = True
        return response

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
        return any([
            request.resolver_match.func.__name__ == 'handle_xblock_callback',
            request.resolver_match.func.__name__ == 'render_xblock',
        ])

    def get_view_path(self, request):
        """ get full import path of match resolver """
        return inspect.getmodule(request.resolver_match.func).__name__

    @classmethod
    def is_installed(cls):
        """ Returns weather this middleware is installed in the running django instance """
        middleware_class_path = sys.modules[cls.__module__].__name__ + '.' + cls.__name__
        middlewares = settings.MIDDLEWARE_CLASSES if hasattr(settings, 'MIDDLEWARE_CLASSES') else settings.MIDDLEWARE
        return middleware_class_path in middlewares
