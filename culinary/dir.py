from . import file
from .core import run


def attribs(location, mode=None, owner=None, group=None, recursive=False):
    """Updates the mode/owner/group for the given remote directory."""
    file.attribs(location, mode, owner, group, recursive)


def exists(location):
    """Tells if there is a remote directory at the given location."""
    return run('test -d "%s" && echo OK ; true' % (location)).endswith("OK")


def remove(location, recursive=True):
    """Removes a directory."""
    flag = ''
    if recursive:
        flag = 'r'
    if exists(location):
        return run('rm -%sf %s && echo OK ; true' % (flag, location))


def ensure(location, recursive=False, mode=None, owner=None, group=None):
    """
    Ensures that there is a remote directory at the given location, optionally
    updating its mode/owner/group.

    If we are not updating the owner/group then this can be done as a single ssh
    call, so use that method, otherwise set owner/group after creation.
    """
    if not exists(location):
        run('mkdir %s "%s" && echo OK ; true' % (recursive and "-p" or "", location))
    if owner or group or mode:
        attribs(location, owner=owner, group=group, mode=mode,
                recursive=recursive)
