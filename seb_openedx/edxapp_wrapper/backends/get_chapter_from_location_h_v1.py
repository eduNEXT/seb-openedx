""" Backend abstraction """
from opaque_keys.edx.keys import UsageKey
from openedx.core.lib.url_utils import unquote_slashes  # pylint: disable=import-error
from xmodule.modulestore.django import modulestore  # pylint: disable=import-error
from xmodule.modulestore import search  # pylint: disable=import-error


def get_chapter_from_location(usage_id, course_key, depth=1):
    """ hawthorn backend """
    usage_key = UsageKey.from_string(unquote_slashes(usage_id)).map_into_course(course_key)
    if usage_key:
        path = search.path_to_location(modulestore(), usage_key)
        chapter = path[depth]  # depth is the position where path_to_location returns the chapter
        return chapter
    return None
