# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pypkgs_xy']

package_data = \
{'': ['*']}

install_requires = \
['pandas>=1.2.2,<2.0.0']

setup_kwargs = {
    'name': 'pypkgs-xy',
    'version': '0.1.0',
    'description': 'toy Python package for DSCI 524 individual assignment 1 by Xudong Yang',
    'long_description': None,
    'author': 'Xudong Yang',
    'author_email': 'xd1222@student.ubc.ca',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
