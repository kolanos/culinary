from .core import run, sudo
from .decorator import dispatch


@dispatch("package")
def upgrade():
    """Updates every package present on the system."""

@dispatch("package")
def update(package=None):
    """
    Updates the package database (when no argument) or update the package or
    list of packages given as argument.
    """


@dispatch("package")
def install(package, update=False):
    """
    Installs the given package/list of package, optionally updating the package
    database.
    """


@dispatch("package")
def ensure(package, update=False):
    """
    Tests if the given package is installed, and installs it in case it's not
    already there. If `update` is true, then the package will be updated if it
    already exists.
    """


@dispatch("package")
def clean(package=None):
    """Clean the repository for un-needed files."""


# -----------------------------------------------------------------------------
# APT PACKAGE (DEBIAN/UBUNTU)
# -----------------------------------------------------------------------------


def update_apt(package=None):
    if package == None:
        sudo("apt-get --yes update")
    else:
        if type(package) in (list, tuple):
            package = " ".join(package)
        sudo('DEBIAN_FRONTEND=noninteractive apt-get --yes -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" upgrade ' + package)


def upgrade_apt():
    sudo('DEBIAN_FRONTEND=noninteractive apt-get --yes -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" upgrade')


def install_apt(package, update=False):
    if update:
        sudo('DEBIAN_FRONTEND=noninteractive apt-get --yes -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" update')
    if type(package) in (list, tuple):
        package = " ".join(package)
    sudo("DEBIAN_FRONTEND=noninteractive apt-get --yes install %s" % (package))


def ensure_apt(package, update=False):
    status = run("dpkg-query -W -f='${Status}' %s ; true" % package)
    if status.find("not-installed") != -1 or status.find("installed") == -1:
        install(package, update)
        return False
    else:
        if update: update(package)
        return True


def clean_apt(package=None):
    pass


# -----------------------------------------------------------------------------
# YUM PACKAGE (RedHat, CentOS)
# added by Prune - 20120408 - v1.0
# -----------------------------------------------------------------------------


def upgrade_yum():
    sudo("yum -y update")


def update_yum(package=None):
    if package == None:
        sudo("yum -y update")
    else:
        if type(package) in (list, tuple):
            package = " ".join(package)
        sudo("yum -y upgrade " + package)


def install_yum(package, update=False):
    if update:
        sudo("yum -y update")
    if type(package) in (list, tuple):
        package = " ".join(package)
    sudo("yum -y install %s" % (package))


def ensure_yum(package, update=False):
    status = run("yum list installed %s ; true" % package)
    if status.find("No matching Packages") != -1 or status.find(package) == -1:
        install(package, update)
        return False
    else:
        if update: update(package)
        return True


def clean_yum(package=None):
    sudo("yum -y clean all")


# -----------------------------------------------------------------------------
# ZYPPER PACKAGE (openSUSE)
# -----------------------------------------------------------------------------


def upgrade_zypper():
    sudo("zypper --non-interactive --gpg-auto-import-keys update --type package")


def update_zypper(package=None):
    if package == None:
        sudo("zypper --non-interactive --gpg-auto-import-keys refresh")
    else:
        if type(package) in (list, tuple):
            package = " ".join(package)
        sudo("zypper --non-interactive --gpg-auto-import-keys update --type package " + package)


def install_zypper(package, update=False):
    if update:
        update_zypper()
    if type(package) in (list, tuple):
        package = " ".join(package)
    sudo("zypper --non-interactive --gpg-auto-import-keys install --type package --name " + package)


def ensure_zypper(package, update=False):
    status = run("zypper --non-interactive --gpg-auto-import-keys search --type package --installed-only --match-exact %s ; true" % package)
    if status.find("No packages found.") != -1 or status.find(package) == -1:
        install_zypper(package)
        return False
    else:
        if update:
            update_zypper(package)
        return True


def clean_zypper():
    sudo("zypper --non-interactive clean")
