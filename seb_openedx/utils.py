""" utils """
import re


def unquote_slashes(text):
    """
    Taken from edx-platform/openedx/core/lib/url_utils.py
    Unquote slashes quoted by `quote_slashes`
    """
    return re.sub(r'(;;|;_)', _unquote_slashes, text)


def _unquote_slashes(match):
    """
    Helper function for `unquote_slashes`
    """
    matched = match.group(0)
    if matched == ';;':
        return ';'
    if matched == ';_':
        return '/'
    return matched
