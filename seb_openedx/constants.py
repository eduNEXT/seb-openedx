"""
Constants for seb-openedx.
"""
SEPARATOR_CHAR = ','

SEB_NOT_TABLES_FOUND = ("SebCourseConfiguration table not found, "
                        "please verify the migrations for the `seb-openedx` app were successfully executed")

SEB_ARRAY_FIELDS_MODEL = [
    'permission_components',
    'browser_keys',
    'config_keys',
    'blacklist_chapters',
    'whitelist_paths',
]
