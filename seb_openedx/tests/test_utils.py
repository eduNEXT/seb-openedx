""" Test utils """
import os


def is_testing_hawthorn():
    """ check if test is running in hawthorn """
    return 'test_hawthorn' in os.environ.get('DJANGO_SETTINGS_MODULE', '')
