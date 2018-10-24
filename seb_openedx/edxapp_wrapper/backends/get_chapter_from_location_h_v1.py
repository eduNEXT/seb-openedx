""" Backend abstraction """
from opaque_keys.edx.keys import UsageKey
from openedx.core.lib.url_utils import unquote_slashes  # pylint: disable=import-error
from xmodule.modulestore.django import modulestore  # pylint: disable=import-error
from xmodule.search import path_to_location  # pylint: disable=import-error


def get_chapter_from_location(usage_id, course_key):
    """ hawthorn backend """
    usage_key = UsageKey.from_string(unquote_slashes(usage_id)).map_into_course(course_key)
    if usage_key:
        path = path_to_location(modulestore(), usage_key)
        chapter_index = 1
        chapter = path[chapter_index]
        return chapter
    return None
