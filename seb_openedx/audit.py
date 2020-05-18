"""Custom audit log for seb_openedx"""

import logging

from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.contrib.contenttypes.models import ContentType
from django.utils import six
from django.db.utils import ProgrammingError
from seb_openedx.constants import SEB_NOT_TABLES_FOUND
from seb_openedx.models import SebCourseConfiguration

LOG = logging.getLogger(__name__)


def get_action(config, instance):
    """Get the action by simulating the normal behavior of the function to_django_model."""
    if config:
        if instance:
            return CHANGE
        return ADDITION
    return DELETION


def get_change_message(data):
    "Get the change message to be displayed in the admin."
    data = {key.lower(): value for key, value in data.items()}  # keys to lowercase
    message = ', '.join(data.keys())
    return 'Changed {}'.format(message)


def get_message(action, config):
    """Choose the message for the admin depending on the action."""
    message = {
        ADDITION: 'Added.',
        CHANGE: get_change_message(config),
        DELETION: 'Deleted.'
    }
    return message.get(action)


def audit_model(func):
    """Decorator to use the LogEntry model from other sources, for the SebCourseConfiguration model."""
    def wrapper(*args, **kwargs):
        """Audits information if it successfully modifies the SebCourseConfiguration model."""
        course_key = args[0]
        config = args[1]
        user_id = kwargs.get('user_id')
        try:
            instance = SebCourseConfiguration.objects.get(course_id=course_key)
        except SebCourseConfiguration.DoesNotExist:
            instance = None
        except ProgrammingError:
            LOG.warning(SEB_NOT_TABLES_FOUND)
            return func(*args, **kwargs)
        action = get_action(config, instance)
        function = func(*args, **kwargs)
        if function:
            if not instance:
                instance = SebCourseConfiguration.objects.get(course_id=course_key)
            LogEntry.objects.log_action(
                user_id=user_id,
                content_type_id=ContentType.objects.get_for_model(SebCourseConfiguration).pk,
                object_id=instance.id,
                object_repr=six.text_type(instance.course_id),
                action_flag=action,
                change_message=get_message(action, config)
            )
        return function
    return wrapper
