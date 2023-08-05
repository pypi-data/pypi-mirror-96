#!/usr/bin/env python3

PROJ_NAME = 'kong-pdk'
PACKAGE_NAME = 'kong_pdk'

PROJ_METADATA = '%s.json' % PROJ_NAME

import os, json, imp
here = os.path.abspath(os.path.dirname(__file__))

try:
    README = open(os.path.join(here, 'README.md')).read()
except:
    README = ""
try:
    CHANGELOG = open(os.path.join(here, 'CHANGELOG.md')).read()
except:
    CHANGELOG = ""
VERSION = imp.load_source('version', os.path.join(here, '%s/const.py' % PACKAGE_NAME)).__version__

packages = [
    'kong_pdk',
]
requires = ['gevent', 'msgpack']

from setuptools import setup

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    description='Kong PDK for Python and Plugin Server',
    long_description=README + '\n\n' + CHANGELOG,
    long_description_content_type="text/markdown",
    author='fffonion',
    author_email='fffonion@gmail.com',
    url='https://github.com/fffonion/kong-python-pdk',
    packages=packages,
    package_dir={'requests': 'requests'},
    include_package_data=True,
    install_requires=requires,
    license='GPLv3',
    zip_safe=False,
    classifiers=(
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: CPython'
    ),
    requires=requires,
    entry_points = {'console_scripts': ["kong-python-pluginserver = kong_pdk.cli:start_server"]},
)