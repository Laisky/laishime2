#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os


def read_requirements():
    """read_requirements returns declared package requirements without private pip APIs."""
    filename = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    with open(filename) as stream:
        return [line.strip() for line in stream
                if line.strip() and not line.lstrip().startswith('#')]


requires = read_requirements()

setup(name='laishime',
      version='2.1.1',
      python_requires='>=3.10',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      install_requires=requires)
