# coding=utf-8
from paver.easy import *
from paver.setuputils import setup
from setuptools import find_packages

setup(
    name="pyage-forams",
    description="Forams package for Pyage platform",
    packages=find_packages(),
    version="0.3.0",
    author="Maciej Kaziród",
    author_email="kazirod.maciej@gmail.com",
    requires=['matplotlib', 'pyage']
)


@task
@needs('generate_setup', 'minilib', 'setuptools.command.sdist')
def sdist():
    """Overrides sdist to make sure that our setup.py is generated."""
    pass


@task
@needs("setuptools.command.bdist_egg")
def egg():
    pass
