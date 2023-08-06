#!/usr/bin/env python
import re
from os import path as op

from setuptools import setup


def _read(fname):
    try:
        return open(op.join(op.dirname(__file__), fname)).read()
    except IOError:
        return ''

_meta = _read('peewee_migrate/__init__.py')
_license = re.search(r'^__license__\s*=\s*"(.*)"', _meta, re.M).group(1)
_project = re.search(r'^__project__\s*=\s*"(.*)"', _meta, re.M).group(1)
_version = re.search(r'^__version__\s*=\s*"(.*)"', _meta, re.M).group(1)

install_requires = [
    l for l in _read('requirements.txt').split('\n')
    if l and not l.startswith('#')]

setup(
    name=_project,
    version=_version,
    license=_license,
    description='Fork of peewee-migrate with active support',
    long_description=_read('README.rst'),
    platforms=('Any'),
    keywords = "django flask sqlalchemy testing mock stub mongoengine data".split(), # noqa
    author='spumer, Kirill Klenov',
    url='https://github.com/spumer/peewee_migrate',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Natural Language :: Russian',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Testing',
        'Topic :: Utilities',
    ],

    packages=['peewee_migrate'],
    include_package_data=True,
    install_requires=install_requires,
    entry_points="""
    [console_scripts]
    pw_migrate=peewee_migrate.cli:cli
    """,
)
