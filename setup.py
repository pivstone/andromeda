# ! /usr/bin/env python
import os
from setuptools import setup

__author__ = 'pivstone'


def get_packages(package):
    """
    Return root package and all sub-packages.
    """
    return [dirpath
            for dirpath, dirnames, filenames in os.walk(package)
            if os.path.exists(os.path.join(dirpath, '__init__.py'))]


def get_package_data(package):
    """
    Return all files under the root package, that are not in a
    package themselves.
    """
    walk = [(dir_path.replace(package + os.sep, '', 1), file_names)
            for dir_path, dir_names, file_names in os.walk(package)
            if not os.path.exists(os.path.join(dir_path, '__init__.py'))]

    file_paths = []
    for base, file_names in walk:
        file_paths.extend([os.path.join(base, filename)
                           for filename in file_names])
    return {package: file_paths}


requirements_txt = open('./requirements/production.txt')
requirements = [line for line in requirements_txt]

setup(name='andromeda',
      version='1.1',
      description='Docker Registry V2 Python Version',
      author=__author__,
      author_email='pivstone@gmail.com',
      packages=get_packages('andromeda'),
      package_data=get_package_data('andromeda'),
      classifiers=['Development Status :: 3 - Alpha',
                   'Intended Audience :: Developers',
                   'Programming Language :: Python :: 3.5',
                   'Programming Language :: Python :: Implementation :: CPython',
                   'Operating System :: OS Independent',
                   'Topic :: Utilities'
                   ],
      zip_safe=False,
      install_requires=requirements,
      )
