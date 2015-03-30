#!/usr/bin/env python
# -*- coding: utf-8 -*-


class LaishimeError(Exception):
    pass


class LaishimeNotCompleted(LaishimeError):
    pass


class LaishimeParseError(LaishimeError):
    pass
