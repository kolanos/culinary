import os.path

from . import dir, file, user
from .core import run


def keygen(user, keytype="dsa"):
    """Generates a pair of ssh keys in the user's home .ssh directory."""
    d = user.check(user)
    assert d, "User does not exist: %s" % (user)
    home = d["home"]
    key_file = home + "/.ssh/id_%s.pub" % keytype
    if not file.exists(key_file):
        dir.ensure(home + "/.ssh", mode="0700", owner=user, group=user)
        run("ssh-keygen -q -t %s -f '%s/.ssh/id_%s' -N ''" %
            (keytype, home, keytype))
        file.attribs(home + "/.ssh/id_%s" % keytype, owner=user, group=user)
        file.attribs(home + "/.ssh/id_%s.pub" % keytype, owner=user,
                     group=user)
        return key_file
    else:
        return key_file


def authorize(user, key):
    """Adds the given key to the '.ssh/authorized_keys' for the given
    user."""
    d = user.check(user)
    keyf = d["home"] + "/.ssh/authorized_keys"
    if key[-1] != "\n":
        key += "\n"
    if file.exists(keyf):
        d = file.read(keyf)
        if file.read(keyf).find(key[:-1]) == -1:
            file.append(keyf, key)
            return False
        else:
            return True
    else:
        # Make sure that .ssh directory exists, see #42
        dir.ensure(os.path.dirname(keyf), owner=user, group=user, mode="700")
        file.write(keyf, key,             owner=user, group=user, mode="600")
        return False
