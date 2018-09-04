""" utils """
import json


def parse_json_maybe(string, default):
    """ Try to parse json, return default if that fails """
    try:
        json_dict = json.loads(string)
    except ValueError:
        json_dict = default
    return json_dict
