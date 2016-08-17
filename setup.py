# ! /usr/bin/env python
import os
from setuptools import setup

__author__ = 'pivstone'


def get_packages(package):
    return [path
            for path, names, files in os.walk(package)
            if os.path.exists(os.path.join(path, '__init__.py'))]


def get_package_data(package):
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
      version='0.2',
      description='Docker Distributions V2 Python Version',
      author=__author__,
      author_email='pivstone@gmail.com',
      packages=get_packages('andromeda'),
      package_data=get_package_data('andromeda'),
      classifiers=['Development Status :: 3 - Beta',
                   'Intended Audience :: Developers',
                   'Programming Language :: Python :: 3.5',
                   'Operating System :: OS Independent',
                   'Topic :: Utilities'
                   ],
      zip_safe=False,
      install_requires=requirements,
      )
