# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pypsql_api',
 'pypsql_api.config',
 'pypsql_api.ext',
 'pypsql_api.wire',
 'pypsql_api.wire.dataframe',
 'pypsql_api.wire.query']

package_data = \
{'': ['*']}

install_requires = \
['pandas>=1.2.2,<2.0.0']

setup_kwargs = {
    'name': 'pypsql-api',
    'version': '0.1.3',
    'description': 'Add postgresql support to your data APIs',
    'long_description': None,
    'author': 'Gerrit Jansen van Vuuren',
    'author_email': 'gerritjvv@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
