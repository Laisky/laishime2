#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import codecs

import yaml

import laishime


PWD = os.path.dirname(laishime.__file__)

with codecs.open(os.path.join(PWD, 'config', 'clean.yml', 'r', 'utf-8')) as fp:
    CONFIGS = yaml.load(fp)
