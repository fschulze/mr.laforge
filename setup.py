import os
from setuptools import setup

version = '0.6'

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
HISTORY = open(os.path.join(here, 'HISTORY.txt')).read()

install_requires = [
    'setuptools',
    'supervisor']

try:
    import argparse
    argparse    # make pyflakes happy...
except ImportError:
    install_requires.append('argparse')

setup(
    name='mr.laforge',
    version=version,
    description="Plugins and utilities for supervisor",
    long_description=README + "\n\n" + HISTORY,
    keywords='',
    author='Florian Schulze',
    author_email='florian.schulze@gmx.net',
    url='http://github.com/fschulze/mr.laforge',
    license='BSD',
    packages=['mr', 'mr.laforge'],
    namespace_packages=['mr'],
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    entry_points="""
    [console_scripts]
    supervisorup = mr.laforge:up
    supervisordown = mr.laforge:down
    waitforports = mr.laforge:waitforports
    """
)
