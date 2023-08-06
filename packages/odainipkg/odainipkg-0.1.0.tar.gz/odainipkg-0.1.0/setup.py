# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['odainipkg']

package_data = \
{'': ['*']}

install_requires = \
['pandas>=1.2.2,<2.0.0']

setup_kwargs = {
    'name': 'odainipkg',
    'version': '0.1.0',
    'description': 'Toy python package',
    'long_description': None,
    'author': 'Asma Al-Odaini',
    'author_email': 'asmaalodaini@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
