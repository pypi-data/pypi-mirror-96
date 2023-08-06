# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['instru']

package_data = \
{'': ['*']}

install_requires = \
['pymodbus>=2.4.0,<3.0.0', 'pyvisa-py>=0.5.1,<0.6.0', 'qcodes>=0.22.0,<0.23.0']

entry_points = \
{'console_scripts': ['demo = instru:main']}

setup_kwargs = {
    'name': 'instru',
    'version': '0.1.23',
    'description': 'Various commonly used instrument drivers',
    'long_description': None,
    'author': 'James Maxwell',
    'author_email': None,
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
