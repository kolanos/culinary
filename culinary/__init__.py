# -*- coding: utf-8 -*-

VERSION = "0.0.1"

from . import option


# Sets up the default options so that @dispatch'ed functions work
def _init():
    for key, value in option.DEFAULT_OPTIONS.items():
        getattr(option, 'select_' + key)(value)

_init()
