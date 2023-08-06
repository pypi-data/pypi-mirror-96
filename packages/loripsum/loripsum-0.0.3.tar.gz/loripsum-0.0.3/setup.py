# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['loripsum']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.1.2,<8.0.0', 'requests>=2.25.1,<3.0.0']

entry_points = \
{'console_scripts': ['loripsum = loripsum.__main__:main']}

setup_kwargs = {
    'name': 'loripsum',
    'version': '0.0.3',
    'description': 'A Python client for lopripsum.net',
    'long_description': None,
    'author': 'Antonio Feregrino',
    'author_email': 'antonio.feregrino@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
