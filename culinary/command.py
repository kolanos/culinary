from .core import run
from .package import install


def check(command):
    """Tests if the given command is available on the system."""
    result = run("which '{0}' >& /dev/null && echo OK ; true".format(command))
    return result.endswith("OK")


def ensure(command, package=None):
    """
    Ensures that the given command is present, if not installs the package with
    the given name, which is the same as the command by default.
    """
    if package is None:
        package = command
    if not check(command):
        install(package)
    assert check(command), \
        "Command was not installed, check for errors: {0}".format(command)
