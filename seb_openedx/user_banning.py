""" Banned users handling module """
import abc
from datetime import datetime
from django.conf import settings
from django.utils import six
from seb_openedx.models import ForbiddenCourseAccess


def is_user_banned(username, course_key):
    """ exposed function to check if user is already banned """
    return _get_back_end().is_user_banned(username, course_key)


def ban_user(username, course_key, banned_by):
    """ exposed function to check if user is already banned """
    last_modified_time = datetime.now()
    _get_back_end().ban_user(username, course_key, last_modified_time, banned_by)


def unban_user(username, course_key, banned_by):
    """ exposed function to check if user is already banned """
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
        return len(ForbiddenCourseAccess.objects.filter(username=username, course_id=course_key, access_blocked=True))  # pylint: disable=no-member

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
