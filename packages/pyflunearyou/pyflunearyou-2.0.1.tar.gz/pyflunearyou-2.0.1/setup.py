# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyflunearyou', 'pyflunearyou.helpers']

package_data = \
{'': ['*']}

install_requires = \
['aiocache>=0.11.1,<0.12.0',
 'aiohttp>=3.7.4,<4.0.0',
 'msgpack>=0.6.2,<1.1.0',
 'ujson>=1.35,<5.0']

setup_kwargs = {
    'name': 'pyflunearyou',
    'version': '2.0.1',
    'description': 'A clean, well-tested Python3 API for Flu Near You',
    'long_description': '# 🤒 pyflunearyou: A Python3 API for Flu Near You\n\n[![CI](https://github.com/bachya/pyflunearyou/workflows/CI/badge.svg)](https://github.com/bachya/pyflunearyou/actions)\n[![PyPi](https://img.shields.io/pypi/v/pyflunearyou.svg)](https://pypi.python.org/pypi/pyflunearyou)\n[![Version](https://img.shields.io/pypi/pyversions/pyflunearyou.svg)](https://pypi.python.org/pypi/pyflunearyou)\n[![License](https://img.shields.io/pypi/l/pyflunearyou.svg)](https://github.com/bachya/pyflunearyou/blob/master/LICENSE)\n[![Code Coverage](https://codecov.io/gh/bachya/pyflunearyou/branch/dev/graph/badge.svg)](https://codecov.io/gh/bachya/pyflunearyou)\n[![Maintainability](https://api.codeclimate.com/v1/badges/dee8556060c7d0e7f2d1/maintainability)](https://codeclimate.com/github/bachya/pyflunearyou/maintainability)\n[![Say Thanks](https://img.shields.io/badge/SayThanks-!-1EAEDB.svg)](https://saythanks.io/to/bachya)\n\n`pyflunearyou` is a simple Python library for retrieving UV-related information\nfrom [Flu Near You](https://flunearyou.org/#!/).\n\n- [Installation](#installation)\n- [Python Versions](#python-versions)\n- [Usage](#usage)\n- [Contributing](#contributing)\n\n# Installation\n\n```python\npip install pyflunearyou\n```\n\n# Python Versions\n\n`pyflunearyou` is currently supported on:\n\n* Python 3.6\n* Python 3.7\n* Python 3.8\n* Python 3.9\n\n# Usage\n\n```python\nimport asyncio\n\nfrom aiohttp import ClientSession\n\nfrom pyflunearyou import Client\n\n\nasync def main() -> None:\n    """Run!"""\n    client = Client()\n\n    # Get user data for a specific latitude/longitude:\n    await client.user_reports.status_by_coordinates(<LATITUDE>, <LONGITUDE>)\n\n    # Get user data for a specific ZIP code:\n    await client.user_reports.status_by_zip("<ZIP_CODE>")\n\n    # Get CDC data for a specific latitude/longitude:\n    await client.cdc_reports.status_by_coordinates(<LATITUDE>, <LONGITUDE>)\n\n    # Get CDC data for a specific state:\n    await client.cdc_reports.status_by_state(\'<USA_CANADA_STATE_NAME>\')\n\nasyncio.run(main())\n```\n\nBy default, the library creates a new connection to Flu Near You with each coroutine. If\nyou are calling a large number of coroutines (or merely want to squeeze out every second\nof runtime savings possible), an\n[`aiohttp`](https://github.com/aio-libs/aiohttp) `ClientSession` can be used for connection\npooling:\n\n```python\nimport asyncio\n\nfrom aiohttp import ClientSession\n\nfrom pyflunearyou import Client\n\n\nasync def main() -> None:\n    """Run!"""\n    async with ClientSession() as session:\n        client = Client(session=session)\n\n        # ...\n\nasyncio.run(main())\n```\n\n# Contributing\n\n1. [Check for open features/bugs](https://github.com/bachya/pyflunearyou/issues)\n  or [initiate a discussion on one](https://github.com/bachya/pyflunearyou/issues/new).\n2. [Fork the repository](https://github.com/bachya/pyflunearyou/fork).\n3. (_optional, but highly recommended_) Create a virtual environment: `python3 -m venv .venv`\n4. (_optional, but highly recommended_) Enter the virtual environment: `source ./.venv/bin/activate`\n5. Install the dev environment: `script/setup`\n6. Code your new feature or bug fix.\n7. Write tests that cover your new functionality.\n8. Run tests and ensure 100% code coverage: `script/test`\n9. Update `README.md` with any new documentation.\n10. Add yourself to `AUTHORS.md`.\n11. Submit a pull request!\n',
    'author': 'Aaron Bach',
    'author_email': 'bachya1208@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/bachya/pyflunearyou',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.1,<4.0.0',
}


setup(**setup_kwargs)
