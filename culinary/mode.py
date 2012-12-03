import fabric.api

MODE_LOCAL = "MODE_LOCAL"
MODE_SUDO = "MODE_SUDO"


class __mode_switcher(object):
    """
    A class that can be used to switch run modes by instanciating the
    class or using it as a context manager.
    """
    MODE_VALUE = True
    MODE_KEY = None

    def __init__(self, value=None):
        self.oldMode = fabric.api.env.get(self.MODE_KEY)
        fabric.api.env[self.MODE_KEY] = self.MODE_VALUE \
                if value is None else value

    def __enter__(self):
        pass

    def __exit__(self, type, value, traceback):
        if self.oldMode is None:
            del fabric.api.env[self.MODE_KEY]
        else:
            fabric.api.env[self.MODE_KEY] = self.oldMode


class local(__mode_switcher):
    """
    Set local mode, where run/sudo won't go through Fabric's API, but directly
    through a popen. This allows you to easily test your scripts without
    using Fabric.
    """
    MODE_KEY = MODE_LOCAL
    MODE_VALUE = True


class remote(__mode_switcher):
    """
    Comes back to Fabric's API for run/sudo. This basically reverts the effect
    of calling `mode_local()`.
    """
    MODE_KEY = MODE_LOCAL
    MODE_VALUE = False


class user(__mode_switcher):
    """Functions will be executed as the current user."""
    MODE_KEY = MODE_SUDO
    MODE_VALUE = False


class sudo(__mode_switcher):
    """Functions will be executed with sudo."""
    MODE_KEY = MODE_SUDO
    MODE_VALUE = True


def mode(key):
    """Queries the given mode (ie. MODE_LOCAL, MODE_SUDO)"""
    return fabric.api.env.get(key, False)


def is_local():
    return mode(MODE_LOCAL)


def is_remote():
    return not mode(MODE_LOCAL)


def is_sudo():
    return mode(MODE_SUDO)
