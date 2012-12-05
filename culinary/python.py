import fabric.api

from .core import run, sudo
from .decorator import dispatch


@dispatch('python package')
def package_upgrade(package):
    """Upgrades the defined python package."""


@dispatch('python package')
def package_install(package=None):
    """Installs the given python package/list of python packages."""


@dispatch('python package')
def package_ensure(package):
    """
    Tests if the given python package is installed, and installes it in
    case it's not already there.
    """


@dispatch('python package')
def package_remove(package):
    """Removes the given python package."""


# -----------------------------------------------------------------------------
# PIP PYTHON PACKAGE MANAGER
# -----------------------------------------------------------------------------


def package_upgrade_pip(package, E=None):
    """
    The "package" argument, defines the name of the package that will be
    upgraded.
    The optional argument "E" is equivalent to the "-E" parameter of pip. E is
    the path to a virtualenv. If provided, it will be added to the pip call.
    """
    if E:
        E = '-E {0}'.format(E)
    else:
        E = ''
    run('pip upgrade {0} {1}'.format(E, package))


def package_install_pip(package=None, r=None, pip=None):
    """
    The "package" argument, defines the name of the package that will be
    installed.
    The argument "r" referes to the requirements file that will be used by pip
    and is equivalent to the "-r" parameter of pip.
    Either "package" or "r" needs to be provided
    The optional argument "E" is equivalent to the "-E" parameter of pip. E is
    the path to a virtualenv. If provided, it will be added to the pip call.
    """
    pip = pip or fabric.api.env.get('pip', 'pip')
    if package:
        run('{0} install {1}'.format(pip, package))
    elif r:
        run('{0} install -r {1}'.format(pip, r))
    else:
        raise Exception("Either a package name or the requirements file has "
                        "to be provided.")


def package_ensure_pip(package=None, r=None, pip=None):
    """
    The "package" argument, defines the name of the package that will be
    ensured.
    The argument "r" referes to the requirements file that will be used by pip
    and is equivalent to the "-r" parameter of pip.
    Either "package" or "r" needs to be provided
    The optional argument "E" is equivalent to the "-E" parameter of pip. E is
    the path to a virtualenv. If provided, it will be added to the pip call.
    """
    # FIXME: At the moment, I do not know how to check for the existence of a
    # pip package and I am not sure if this really makes sense, based on the
    # pip built in functionality.
    # So I just call the install functions
    pip = pip or fabric.api.env.get('pip', 'pip')
    package_install_pip(package, r, pip)


def package_remove_pip(package, E=None, pip=None):
    """
    The "package" argument, defines the name of the package that will be
    ensured.
    The argument "r" referes to the requirements file that will be used by pip
    and is equivalent to the "-r" parameter of pip.
    Either "package" or "r" needs to be provided
    The optional argument "E" is equivalent to the "-E" parameter of pip. E is
    the path to a virtualenv. If provided, it will be added to the pip call.
    """
    pip = pip or fabric.api.env.get('pip', 'pip')
    return run('{0} uninstall {1}'.format(pip, package))


# -----------------------------------------------------------------------------
# EASY_INSTALL PYTHON PACKAGE MANAGER
# -----------------------------------------------------------------------------


def package_upgrade_easy_install(package):
    """
    The "package" argument, defines the name of the package that will be
    upgraded.
    """
    run('easy_install --upgrade {0}'.format(package))


def package_install_easy_install(package):
    """
    The "package" argument, defines the name of the package that will be
    installed.
    """
    sudo('easy_install {0}'.format(package))


def package_ensure_easy_install(package):
    """
    The "package" argument, defines the name of the package that will be
    ensured.
    """
    # FIXME: At the moment, I do not know how to check for the existence of a
    # py package and I am not sure if this really makes sense, based on the
    # easy_install built in functionality.
    # So I just call the install functions
    package_install_easy_install(package)


def package_remove_easy_install(package):
    """
    The "package" argument, defines the name of the package that will be
    removed.
    """
    # FIXME: this will not remove egg file etc.
    run('easy_install -m {0}'.format(package))
