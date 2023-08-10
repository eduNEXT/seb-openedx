"""
API v1 serializers.
"""
from __future__ import absolute_import, unicode_literals

from rest_framework import serializers


# pylint: disable=abstract-method
class SebConfigurationSerializer(serializers.Serializer):
    """
    Converts a SEB configuration from a json into a validated python dict

    An example of one of the most complex configurations currently supported
    {
        "BROWSER_KEYS":[
            "cd8827e4555e4eef825088a4bd5c9887f32e590"
        ],
        "CONFIG_KEYS":[
            "9887f32e590cd8827e5088a4bd5c4555e4eef82"
        ],
        "PERMISSION_COMPONENTS":[
            "AlwaysAllowStaff",
        ],
        "USER_BANNING_ENABLED": True,
    }
    """
    BROWSER_KEYS = serializers.ListField(
        child=serializers.RegexField(r"^[a-zA-Z0-9]+$"),
        required=False,
    )
    CONFIG_KEYS = serializers.ListField(
        child=serializers.RegexField(r"^[a-zA-Z0-9]+$"),
        required=False,
    )
    PERMISSION_COMPONENTS = serializers.ListField(
        child=serializers.ChoiceField(
            choices=[
                "AlwaysAllowStaff",
                "AlwaysDenyAccess",
                "AlwaysGrantAccess",
                "CheckSEBHashConfigKey",
                "CheckSEBHashBrowserExamKey",
                "CheckSEBHashBrowserExamKeyOrConfigKey",
            ],
        ),
        required=False,
    )
    USER_BANNING_ENABLED = serializers.BooleanField(required=False)
