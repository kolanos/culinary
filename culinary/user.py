import base64

from . import group
from .core import sudo


def passwd(name, passwd, encrypted_passwd=False):
    """Sets the given user password."""
    encoded_password = base64.b64encode("{0}:{1}".format(name, passwd))
    encryption = " -e" if encrypted_passwd else ""
    sudo("echo {0} | base64 --decode | chpasswd{1}".format(encoded_password,
                                                           encryption))


def create(name, passwd=None, home=None, uid=None, gid=None, shell=None,
                uid_min=None, uid_max=None, encrypted_passwd=False):
    """
    Creates the user with the given name, optionally giving a specific
    password/home/uid/gid/shell.
    """
    options = ["-m"]
    if home:
        options.append("-d '{0}'".format(home))
    if uid:
        options.append("-u '{0}'".format(uid))
    # If group exists already but is not specified, useradd fails.
    if not gid and group.check(name):
        gid = name
    if gid:
        options.append("-g '{0}'".format(gid))
    if shell:
        options.append("-s '{0}'".format(shell))
    if uid_min:
        options.append("-K UID_MIN='{0}'".format(uid_min))
    if uid_max:
        options.append("-K UID_MAX='{0}'".format(uid_max))
    sudo("useradd {0} '{1}'".format(" ".join(options), name))
    if passwd:
        passwd(name, passwd, encrypted_passwd)


def check(name=None, uid=None):
    """
    Checks if there is a user defined with the given name, returning its
    information as a '{"name": <str>, "uid": <str>, "gid": <str>, "home":
    <str>, "shell": <str>}' or 'None' if the user does not exists.
    """
    assert name != None or uid != None, \
            "check: either `uid` or `name` should be given"
    assert name is None or uid is None, \
            "check: `uid` and `name` both given, only one should be provided"
    if name != None:
        d = sudo("cat /etc/passwd | egrep '^{0}:' ; true".format(name))
    elif uid != None:
        d = sudo("cat /etc/passwd | egrep '^.*:.*:{0}:' ; true".format(uid))
    results = {}
    s = None
    if d:
        d = d.split(":")
        assert len(d) >= 7, \
                ("/etc/passwd entry is expected to have at least 7 fields, "
                 "got {0} in: {1}").format(len(d), ":".join(d))
        results = dict(name=d[0], uid=d[2], gid=d[3], home=d[5], shell=d[6])
        s = sudo(("cat /etc/shadow | egrep '^{0}:' | awk -F':' "
                  "'{print $2}'").format(results['name']))
        if s:
            results['passwd'] = s
    if results:
        return results
    else:
        return None


def ensure(name, passwd=None, home=None, uid=None, gid=None, shell=None):
    """
    Ensures that the given users exists, optionally updating their
    passwd/home/uid/gid/shell.
    """
    d = check(name)
    if not d:
        create(name, passwd, home, uid, gid, shell)
    else:
        options = []
        if home != None and d.get("home") != home:
            options.append("-d '{0}'".format(home))
        if uid != None and d.get("uid") != uid:
            options.append("-u '{0}'".format(uid))
        if gid != None and d.get("gid") != gid:
            options.append("-g '{0}'".format(gid))
        if shell != None and d.get("shell") != shell:
            options.append("-s '{0}'".format(shell))
        if options:
            sudo("usermod {0} '{1}'".format(" ".join(options), name))
        if passwd:
            passwd(name, passwd)


def remove(name, rmhome=None):
    """
    Removes the user with the given name, optionally removing the home
    directory and mail spool.
    """
    options = ["-f"]
    if rmhome:
        options.append("-r")
    sudo("userdel {0} '{1}'".format(" ".join(options), name))
