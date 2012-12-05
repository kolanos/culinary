# -*- coding: utf-8 -*-

__version__ = "0.1.0"

from . import (command, core, dir, file, group, misc, mode, option, package,
               process, python, repository, ssh, text, user)


# Sets up the default options so that @dispatch'ed functions work.
def _init():
    for key, value in option.DEFAULT_OPTIONS.items():
        getattr(option, 'select_{0}'.format(key))(value)

_init()
