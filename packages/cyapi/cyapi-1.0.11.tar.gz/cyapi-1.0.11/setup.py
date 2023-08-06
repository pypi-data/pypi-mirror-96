# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cyapi', 'cyapi.mixins']

package_data = \
{'': ['*'], 'cyapi': ['exclusions/*', 'reqs/*']}

install_requires = \
['pyjwt', 'python-dateutil', 'pytz', 'requests', 'tqdm']

extras_require = \
{':python_version == "2.7"': ['futures']}

setup_kwargs = {
    'name': 'cyapi',
    'version': '1.0.11',
    'description': 'Python bindings for Cylance Console and MTC',
    'long_description': '# Summary\n\nThis Library provides python bindings to interact with the Cylance API. Examples have been created for you in the Examples/ directory, and provide a majority of the common code you\'ll need to get setup. In order to utilize this Library, you will need an API token from the API Integrations tab inside of the Cylance Console.\n\n# Supported Systems\n* Python 2.7 & Python 3 Compatible\n* Windows\n* Mac\n* Linux\n\n# Installation\n\n```\npip install cyapi\n```\n\n# Example\n\nPlease note there are a number of example scripts in the examples directory. These are valuable for initial authentication as well as some basic interactions with the library. The example scripts include:\nSingle Tenant\n> simple_setup.py\n> find_stale_devices.py\n> safelist_trusted_local.py\n> time_getting_all_detection_detail.py\n\nMulti-Tenant Console (MTC)\n> simple_MTC_setup.py\n> MTC_tenants_loop.py\n\nThis example will create a connection to the API and return all devices that have registered.\n\n```\nfrom cyapi.cyapi import CyAPI\nfrom pprint import pprint\nAPI = CyAPI(tid=your_id, aid=your_aid, ase=your_ase)\nAPI.create_conn()\ndevices = API.get_devices()\nprint("Successful: {}".format(devices.is_success))\npprint(devices.data[0]) # Print info about a single device.\n```\n\nIf you have lots of devices/threats/zones/etc, and you\'d like to see a progress bar, pass the `disable_progress` parameter:\n\n```\ndevices = API.get_devices(disable_progress=False)\npprint(devices.data[0])\n```\n\nAdditionally you can copy examples/simple_setup.py to your_new_file.py and begin hacking away from there.\n\n# Creds File\n\nYou can create a file that will store your api credentials instead of passing them in via the command line. The creds file should look like the following:\n\nFor a standard tenant:\ncreds.json:\n```\n{\n    "tid": "123456-55555-66666-888888888",\n    "app_id": "11111111-222222-33333-44444444",\n    "app_secret": "555555-666666-222222-444444",\n    "region": "NA"\n}\n```\n\nFor a Multi-Tenant Console (MTC)\n```\n{\n    "tid": "Not Used for MTC Auth",\n    "app_id": "11111111-222222-33333-44444444",\n    "app_secret": "555555-666666-222222-444444",\n    "region": "NA",\n    "mtc": "True"\n}\n```\nThe creds json file can then be passed in by passing -c path/to/creds.json to any of the examples\n\n# API End Point Documentation\n\nTenant User API Guide - https://docs.blackberry.com/content/dam/docs-blackberry-com/release-pdfs/en/cylance-products/api-and-developer-guides/Cylance%20User%20API%20Guide%20v2.0%20rev24.pdf\nTenant User API Release Notes - https://docs.blackberry.com/en/unified-endpoint-security/cylance--products/cylance-api-release-notes/BlackBerry-Cylance-API-release-notes\nMulti-Tenant API - https://dev-admin.cylance.com/documentation/api.html\n\n# Contributing\n\nSee [CONTRIBUTING.md](CONTRIBUTING.md)\n',
    'author': 'Shane Shellenbarger',
    'author_email': 'soggysec@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/cylance/python-cyapi',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
}


setup(**setup_kwargs)
