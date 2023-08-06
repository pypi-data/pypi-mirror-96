# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fivetwofour_assignment_1']

package_data = \
{'': ['*']}

install_requires = \
['pandas>=1.2.2,<2.0.0']

setup_kwargs = {
    'name': 'fivetwofour-assignment-1',
    'version': '0.1.0',
    'description': 'Python package for DSCI 524 Assignment 1',
    'long_description': None,
    'author': 'Charles Suresh',
    'author_email': 'emailcharlesjosh@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
