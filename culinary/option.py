import fabric.api

OPTION_PACKAGE = "OPTION_PACKAGE"
OPTION_PYTHON_PACKAGE = "OPTION_PYTHON_PACKAGE"
AVAILABLE_OPTIONS = dict(
    package=["apt", "yum", "zypper"],
    python_package=["easy_install", "pip"]
)
DEFAULT_OPTIONS = dict(
    package="apt",
    python_package="pip"
)


def select_package(selection=None):
    """Selects the type of package subsystem to use (ex:apt, yum or zypper)."""
    supported = AVAILABLE_OPTIONS["package"]
    if selection is not None:
        assert selection in supported, \
                "Option must be one of: %s" % (supported)
        fabric.api.env[OPTION_PACKAGE] = selection
    return (fabric.api.env[OPTION_PACKAGE], supported)


def select_python_package(selection=None):
    supported = AVAILABLE_OPTIONS["python_package"]
    if not (selection is None):
        assert selection in supported, \
                "Option must be one of: %s" % (supported)
        fabric.api.env[OPTION_PYTHON_PACKAGE] = selection
    return (fabric.api.env[OPTION_PYTHON_PACKAGE], supported)
