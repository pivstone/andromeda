import os

__author__ = 'pivstone'


def ensure_dir(file_name):
    dir_name = os.path.dirname(file_name)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
