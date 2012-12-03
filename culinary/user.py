import base64

from . import group
from .core import sudo


def passwd(name, passwd, encrypted_passwd=False):
    """Sets the given user password."""
    encoded_password = base64.b64encode("%s:%s" % (name, passwd))
    encryption = " -e" if encrypted_passwd else ""
    sudo("echo %s | base64 --decode | chpasswd%s" \
            % (encoded_password, encryption))


def create(name, passwd=None, home=None, uid=None, gid=None, shell=None,
                uid_min=None, uid_max=None, encrypted_passwd=False):
    """Creates the user with the given name, optionally giving a
    specific password/home/uid/gid/shell."""
    options = ["-m"]
    if home:
        options.append("-d '%s'" % (home))
    if uid:
        options.append("-u '%s'" % (uid))
    #if group exists already but is not specified, useradd fails
    if not gid and group.check(name):
        gid = name
    if gid:
        options.append("-g '%s'" % (gid))
    if shell:
        options.append("-s '%s'" % (shell))
    if uid_min:
        options.append("-K UID_MIN='%s'" % (uid_min))
    if uid_max:
        options.append("-K UID_MAX='%s'" % (uid_max))
    sudo("useradd %s '%s'" % (" ".join(options), name))
    if passwd:
        passwd(name, passwd, encrypted_passwd)


def check(name=None, uid=None):
    """Checks if there is a user defined with the given name,
    returning its information as a
    '{"name":<str>,"uid":<str>,"gid":<str>,"home":<str>,"shell":<str>}'
    or 'None' if the user does not exists."""
    assert name != None or uid != None, \
            "check: either `uid` or `name` should be given"
    assert name is None or uid is None, \
            "check: `uid` and `name` both given, only one should be provided"
    if   name != None:
        d = sudo("cat /etc/passwd | egrep '^%s:' ; true" % (name))
    elif uid != None:
        d = sudo("cat /etc/passwd | egrep '^.*:.*:%s:' ; true" % (uid))
    results = {}
    s = None
    if d:
        d = d.split(":")
        assert len(d) >= 7, \
                ("/etc/passwd entry is expected to have at least 7 fields, "
                 "got %s in: %s") % (len(d), ":".join(d))
        results = dict(name=d[0], uid=d[2], gid=d[3], home=d[5], shell=d[6])
        s = sudo("cat /etc/shadow | egrep '^%s:' | awk -F':' '{print $2}'" \
                % (results['name']))
        if s:
            results['passwd'] = s
    if results:
        return results
    else:
        return None


def ensure(name, passwd=None, home=None, uid=None, gid=None, shell=None):
    """Ensures that the given users exists, optionally updating their
    passwd/home/uid/gid/shell."""
    d = check(name)
    if not d:
        create(name, passwd, home, uid, gid, shell)
    else:
        options = []
        if home != None and d.get("home") != home:
            options.append("-d '%s'" % (home))
        if uid != None and d.get("uid") != uid:
            options.append("-u '%s'" % (uid))
        if gid != None and d.get("gid") != gid:
            options.append("-g '%s'" % (gid))
        if shell != None and d.get("shell") != shell:
            options.append("-s '%s'" % (shell))
        if options:
            sudo("usermod %s '%s'" % (" ".join(options), name))
        if passwd:
            passwd(name, passwd)


def remove(name, rmhome=None):
    """Removes the user with the given name, optionally
    removing the home directory and mail spool."""
    options = ["-f"]
    if rmhome:
        options.append("-r")
    sudo("userdel %s '%s'" % (" ".join(options), name))
