from __future__ import with_statement

import StringIO
import subprocess

import fabric.api

from . import mode

SUDO_PASSWORD = "SUDO_PASSWORD"


def sudo_password(password=None):
    """Sets the password for the sudo command."""
    if password is None:
        return fabric.api.env.get(SUDO_PASSWORD)
    else:
        if not password:
            del fabric.api.env[SUDO_PASSWORD]
        else:
            fabric.api.env[SUDO_PASSWORD] = password


def run_local(command, sudo=False, shell=True, pty=True, combine_stderr=None):
    """
    Local implementation of fabric.api.run() using subprocess.

    Note: pty option exists for function signature compatibility and is
    ignored.
    """
    if combine_stderr is None:
        combine_stderr = fabric.api.env.combine_stderr
    # TODO: Pass the SUDO_PASSWORD variable to the command here
    if sudo:
        command = "sudo " + command
    stderr = subprocess.STDOUT if combine_stderr else subprocess.PIPE
    process = subprocess.Popen(command, shell=shell, stdout=subprocess.PIPE,
                               stderr=stderr)
    out, err = process.communicate()
    # FIXME: Should stream the output, and only print it if fabric's properties
    # allow it print out Wrap stdout string and add extra status attributes.
    result = fabric.operations._AttributeString(out.rstrip('\n'))
    result.return_code = process.returncode
    result.succeeded = process.returncode == 0
    result.failed = not result.succeeded
    result.stderr = StringIO.StringIO(err)
    return result


def run(*args, **kwargs):
    """
    A wrapper to Fabric's run/sudo commands that takes into account the
    `MODE_LOCAL` and `MODE_SUDO` modes.
    """
    if mode.is_local():
        if mode.is_sudo():
            kwargs.setdefault("sudo", True)
        return run_local(*args, **kwargs)
    else:
        if mode.is_sudo():
            return fabric.api.sudo(*args, **kwargs)
        else:
            return fabric.api.run(*args, **kwargs)


def sudo(*args, **kwargs):
    """
    A wrapper to Fabric's run/sudo commands, using the 'mode.MODE_SUDO'
    global to tell whether the command should be run as regular user or sudo.
    """
    with mode.sudo():
        return run(*args, **kwargs)
