""" Backend abstraction """
from xmodule.modulestore import ModuleStoreEnum  # pylint: disable=import-error
from xmodule.modulestore.django import modulestore  # pylint: disable=import-error


def get_course_module(course_key, depth=0):
    """ get_course_module backend """
    return modulestore().get_course(course_key, depth=0)


def modulestore_update_item(course_key, course_module, user_id):
    """
    update_item backend.
    Updates both the draft and published branches.
    """
    with modulestore().bulk_operations(course_key):
        with modulestore().branch_setting(ModuleStoreEnum.Branch.draft_preferred):
            modulestore().update_item(course_module, user_id)
        return modulestore().update_item(course_module, user_id)
