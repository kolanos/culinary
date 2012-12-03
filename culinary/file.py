from __future__ import with_statement

import base64
import hashlib
import os
import tempfile
import zlib

import fabric.api
import fabric.operations

from . import mode
from .core import run


def local_read(location):
    """
    Reads a *local* file from the given location, expanding '~' and shell
    variables.
    """
    p = os.path.expandvars(os.path.expanduser(location))
    f = file(p, 'rb')
    t = f.read()
    f.close()
    return t


def read(location):
    """Reads the *remote* file at the given location."""
    # NOTE: We use base64 here to be sure to preserve the encoding
    # (UNIX/DOC/MAC) of EOLs
    return base64.b64decode(run('cat "%s" | base64' % (location)))


def exists(location):
    """Tests if there is a *remote* file at the given location."""
    return run('test -e "%s" && echo OK ; true' % (location)).endswith("OK")


def is_file(location):
    return run("test -f '%s' && echo OK ; true" % (location)).endswith("OK")


def is_dir(location):
    return run("test -d '%s' && echo OK ; true" % (location)).endswith("OK")


def is_link(location):
    return run("test -L '%s' && echo OK ; true" % (location)).endswith("OK")


def attribs(location, mode=None, owner=None, group=None, recursive=False):
    """Updates the mode/owner/group for the remote file at the given
    location."""
    recursive = recursive and "-R " or ""
    if mode:
        run('chmod %s %s "%s"' % (recursive, mode,  location))
    if owner:
        run('chown %s %s "%s"' % (recursive, owner, location))
    if group:
        run('chgrp %s %s "%s"' % (recursive, group, location))


def attribs_get(location):
    """Return mode, owner, and group for remote path.
    Return mode, owner, and group if remote path exists, 'None'
    otherwise.
    """
    if exists(location):
        fs_check = run('stat %s %s' % (location, '--format="%a %U %G"'))
        (mod, owner, group) = fs_check.split(' ')
        return {'mode': mod, 'owner': owner, 'group': group}
    else:
        return None


def write(location, content, mode=None, owner=None, group=None, sudo=None,
          check=True):
    """Writes the given content to the file at the given remote
    location, optionally setting mode/owner/group."""
    # FIXME: Big files are never transferred properly!
    # Gets the content signature and write it to a secure tempfile
    use_sudo = sudo if sudo is not None else mode.is_sudo()
    sig = hashlib.sha256(content).hexdigest()
    fd, local_path = tempfile.mkstemp()
    os.write(fd, content)
    # Upload the content if necessary
    if not exists(location) or sig != sha256(location):
        if mode.is_local():
            with mode.sudo(use_sudo):
                run('cp "%s" "%s"' % (local_path, location))
        else:
            # FIXME: Put is not working properly, I often get stuff like:
            # Fatal error: sudo() encountered an error (return code 1) while
            # executing 'mv "3dcf7213c3032c812769e7f355e657b2df06b687"
            # "/etc/authbind/byport/80"'
            #fabric.operations.put(local_path, location, use_sudo=use_sudo)
            # Hides the output, which is especially important
            with fabric.context_managers.settings(
                fabric.api.hide('warnings', 'running', 'stdout'),
                warn_only=True,
                **{mode.MODE_SUDO: use_sudo}
            ):
                # See:
                # http://unix.stackexchange.com/questions/22834/how-to-uncompress-zlib-data-in-unix
                with mode.sudo(use_sudo):
                    result = run(("echo '%s' | base64 --decode | openssl "
                                  "zlib -d > \"%s\"") \
                                  % (base64.b64encode(zlib.compress(content)),
                                     location))
                if result.failed:
                    fabric.api.abort(('Encountered error writing the file '
                                      '%s: %s') % (location, result))

    # Remove the local temp file
    os.close(fd)
    os.unlink(local_path)
    # Ensures that the signature matches
    if check:
        with mode.sudo(use_sudo):
            sig = sha256(location)
        assert sig == sig, \
                "File content does not matches file: %s, got %s, expects %s" \
                % (location, repr(sig), repr(sig))
    with mode.sudo(use_sudo):
        attribs(location, mode=mode, owner=owner, group=group)


def ensure(location, mode=None, owner=None, group=None):
    """Updates the mode/owner/group for the remote file at the given
    location."""
    if exists(location):
        attribs(location, mode=mode, owner=owner, group=group)
    else:
        write(location, "", mode=mode, owner=owner, group=group)


def upload(remote, local, sudo=None):
    """
    Uploads the local file to the remote location only if the remote location
    does not exists or the content are different.
    """
    # FIXME: Big files are never transferred properly!
    # XXX: this 'sudo' kw arg shadows the function named 'sudo'
    use_sudo = mode.is_sudo() or sudo
    f = open(local, 'rb')
    content = f.read()
    f.close()
    sig = hashlib.sha256(content).hexdigest()
    if not exists(remote) or sig != sha256(remote):
        if mode.is_local():
            if use_sudo:
                sudo('cp "%s" "%s"' % (local, remote))
            else:
                run('cp "%s" "%s"' % (local, remote))
        else:
            fabric.operations.put(local, remote, use_sudo=use_sudo)


def update(location, updater=lambda x: x):
    """Updates the content of the given by passing the existing
    content of the remote file at the given location to the 'updater'
    function.

    For instance, if you'd like to convert an existing file to all
    uppercase, simply do:

    >   update("/etc/myfile", lambda _:_.upper())
    """
    assert exists(location), "File does not exists: " + location
    new_content = updater(read(location))
    # assert type(new_content) in (str, unicode,
    # fabric.operations._AttributeString), "Updater must be like
    # (string)->string, got: %s() = %s" %  (updater, type(new_content))
    run('echo "%s" | base64 -d > "%s"' \
            % (base64.b64encode(new_content), location))


def append(location, content, mode=None, owner=None, group=None):
    """Appends the given content to the remote file at the given
    location, optionally updating its mode/owner/group."""
    run('echo "%s" | base64 -d >> "%s"' \
            % (base64.b64encode(content), location))
    attribs(location, mode, owner, group)


def unlink(path):
    if exists(path):
        run("unlink '%s'" % (path))


def link(source, destination, symbolic=True, mode=None, owner=None,
         group=None):
    """
    Creates a (symbolic) link between source and destination on the remote
    host. optionally setting its mode/owner/group.
    """
    if exists(destination) and (not is_link(destination)):
        raise Exception("Destination already exists and is not a link: %s" \
                % (destination))
    # FIXME: Should resolve the link first before unlinking
    if is_link(destination):
        unlink(destination)
    if symbolic:
        run('ln -sf "%s" "%s"' % (source, destination))
    else:
        run('ln -f "%s" "%s"' % (source, destination))
    attribs(destination, mode, owner, group)


def sha256(location):
    """
    Returns the SHA-256 sum (as a hex string) for the remote file at the given
    location.
    """
    # NOTE: In some cases, sudo can output errors in here -- but the errors
    # will appear before the result, so we simply split and get the last
    # line to be on the safe side.
    sig = run('shasum -a 256 "%s" | cut -d" " -f1' % (location)).split("\n")
    return sig[-1].strip()
