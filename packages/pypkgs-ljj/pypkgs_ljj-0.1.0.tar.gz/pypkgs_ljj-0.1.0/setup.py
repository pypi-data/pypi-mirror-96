# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pypkgs_ljj']

package_data = \
{'': ['*']}

install_requires = \
['pandas>=1.2.2,<2.0.0']

setup_kwargs = {
    'name': 'pypkgs-ljj',
    'version': '0.1.0',
    'description': 'Python package that eases the pain of concatenating Pandas categoricals!',
    'long_description': None,
    'author': 'jiajie0225',
    'author_email': 'jiajielim97@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
