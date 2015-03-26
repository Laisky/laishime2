#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from pip.req import parse_requirements
from pip.download import PipSession


requires = [str(i.req) for i in parse_requirements('requirements.txt',
                                                   session=PipSession())
            if i.req is not None]


setup(name='laishime',
      version='2.1.1',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      install_requires=requires)
