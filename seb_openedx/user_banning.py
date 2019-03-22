""" Banned users handling module """
import abc
from datetime import datetime
from django.conf import settings
from django.utils import six
from seb_openedx.models import ForbiddenCourseAccess
from seb_openedx.seb_keys_sources import get_config_by_course


def is_user_banning_enabled(course_key=None):
    """
    Wrapper function to find the status of the banning feature per course or globally
    """
    _config = get_config_by_course(course_key)
    return _config.get('USER_BANNING_ENABLED', settings.SEB_USER_BANNING_ENABLED)


def is_user_banned(username, course_key):
    """
    Public function to check if user is already banned

    The function will return False if the feature is turned off for a given course
    """
    if not username:
        return False

    return (
        is_user_banning_enabled(course_key) and _get_back_end().is_user_banned(username, course_key)
    )


def ban_user(username, course_key, banned_by):
    """
    Public function to ban user.

    Returns a tuple containing boolean values
        - is the user banned
        - is this a new ban
    """
    if not username:
        return (False, False,)

    if not is_user_banning_enabled(course_key):
        return (False, False)

    if is_user_banned(username, course_key):
        return (True, False,)

    last_modified_time = datetime.now()
    _get_back_end().ban_user(username, course_key, last_modified_time, banned_by)
    return (True, True,)


def unban_user(username, course_key, banned_by):
    """
    Public function to remove the ban on a given user
    """
    last_modified_time = datetime.now()
    _get_back_end().unban_user(username, course_key, last_modified_time, banned_by)


def get_all_banning_data():
    """ exposed function to get the data list of banned/unbanned user """
    return _get_back_end().get_all_banning_data()


@six.add_metaclass(abc.ABCMeta)
class BannedUsersBackend(object):
    """ Abstract BannedUserBackend class """

    @abc.abstractmethod
    def is_user_banned(self, username, course_key):
        """ is_user_banned abstract method """
        pass

    @abc.abstractmethod
    def ban_user(self, username, course_key, last_modified_time, banned_by):
        """ is_user_banned abstract method """
        pass

    @abc.abstractmethod
    def unban_user(self, username, course_key, last_modified_time, unbanned_by):
        """ is_user_banned abstract method """
        pass

    @abc.abstractmethod
    def get_all_banning_data(self):
        """ get_all_banning_data abstract method """
        pass


class DatabaseBannedUsersBackend(BannedUsersBackend):
    """ Database backend """
    def is_user_banned(self, username, course_key):
        """ Check if row exists on the database (ForbiddenCourseAccess) """
        return len(ForbiddenCourseAccess.objects.filter(  # pylint: disable=no-member
            username=username,
            course_id=course_key,
            access_blocked=True
        ))

    def ban_user(self, username, course_key, last_modified_time, banned_by):
        """ Create or update forbidden_access, set access_blocked=True """
        forbidden_access, created = ForbiddenCourseAccess.objects.get_or_create(  # pylint: disable=unused-variable
            username=username,
            course_id=course_key,
        )
        forbidden_access.access_blocked = True
        forbidden_access.last_modified_time = last_modified_time
        forbidden_access.last_modified_by_username = banned_by
        forbidden_access.save()

    def unban_user(self, username, course_key, last_modified_time, unbanned_by):
        """ Update forbidden access row, set access_blocked=False """
        forbidden_access = ForbiddenCourseAccess.objects.filter(username=username, course_id=course_key).first()
        forbidden_access.access_blocked = False
        forbidden_access.last_modified_time = last_modified_time
        forbidden_access.last_modified_by_username = unbanned_by
        forbidden_access.save()

    def get_all_banning_data(self):
        return ForbiddenCourseAccess.objects.all()


class UserprofileBannedUsersBackend(BannedUsersBackend):
    """ Userprofile backend """
    def is_user_banned(self, username, course_key):
        """ is_user_banned implementation """
        raise NotImplementedError()

    def ban_user(self, username, course_key, last_modified_time, banned_by):
        """ ban_user implementation """
        raise NotImplementedError()

    def unban_user(self, username, course_key, last_modified_time, unbanned_by):
        """ ban_user implementation """
        raise NotImplementedError()

    def get_all_banning_data(self):
        """ get_all_banning_data implementation """
        raise NotImplementedError()


def _get_back_end():
    """ get back end util """
    backend = globals()[getattr(settings, 'SEB_USER_BANNING_BACKEND')]
    return backend()
