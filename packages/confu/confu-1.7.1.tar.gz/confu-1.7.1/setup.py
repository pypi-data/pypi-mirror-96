# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['confu', 'confu.schema']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'confu',
    'version': '1.7.1',
    'description': 'Configuration file validation and generation',
    'long_description': None,
    'author': '20C',
    'author_email': 'code@20c.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/20c/confu',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
