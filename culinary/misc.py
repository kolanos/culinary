from __future__ import with_statement

import fabric

from . import file, mode, text
from .core import sudo


def upstart_ensure(name):
    """
    Ensures that the given upstart service is running, restarting it if
    necessary.
    """
    with fabric.api.settings(warn_only=True):
        status = sudo("service %s status" % name)
    if status.failed:
        sudo("service %s start" % name)
    else:
        sudo("service %s restart" % name)


def system_uuid_alias_add():
    """
    Adds system UUID alias to /etc/hosts.
    Some tools/processes rely/want the hostname as an alias in
    /etc/hosts e.g. `127.0.0.1 localhost <hostname>`.
    """
    with mode.sudo():
        old = "127.0.0.1 localhost"
        new = old + " " + system_uuid()
        file.update('/etc/hosts', lambda x: text.replace_line(x, old, new)[0])


def system_uuid():
    """Gets a machines UUID (Universally Unique Identifier)."""
    return sudo('dmidecode -s system-uuid | tr "[A-Z]" "[a-z]"')


# Only tested on Ubuntu!
def locale_check(locale):
    locale_data = sudo("locale -a | egrep '^%s$' ; true" % (locale,))
    return locale_data == locale


def locale_ensure(locale):
    if not locale_check(locale):
        with fabric.context_managers.settings(warn_only=True):
            sudo("/usr/share/locales/install-language-pack %s" % (locale,))
        sudo("dpkg-reconfigure locales")
