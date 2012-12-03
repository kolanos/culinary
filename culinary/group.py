from .core import run, sudo


def create(name, gid=None):
    """Creates a group with the given name, and optionally given gid."""
    options = []
    if gid:
        options.append("-g '%s'" % (gid))
    sudo("groupadd %s '%s'" % (" ".join(options), name))


def check(name):
    """Checks if there is a group defined with the given name,
    returning its information as a
    '{"name":<str>,"gid":<str>,"members":<list[str]>}' or 'None' if
    the group does not exists."""
    group_data = run("cat /etc/group | egrep '^%s:' ; true" % (name))
    if group_data:
        name, _, gid, members = group_data.split(":", 4)
        return dict(name=name, gid=gid,
                    members=tuple(m.strip() for m in members.split(",")))
    else:
        return None


def ensure(name, gid=None):
    """Ensures that the group with the given name (and optional gid)
    exists."""
    d = check(name)
    if not d:
        create(name, gid)
    else:
        if gid != None and d.get("gid") != gid:
            sudo("groupmod -g %s '%s'" % (gid, name))


def user_check(group, user):
    """Checks if the given user is a member of the given group. It
    will return 'False' if the group does not exist."""
    d = check(group)
    if d is None:
        return False
    else:
        return user in d["members"]


def user_add(group, user):
    """Adds the given user/list of users to the given group/groups."""
    assert check(group), "Group does not exist: %s" % (group)
    if not user_check(group, user):
        sudo("usermod -a -G '%s' '%s'" % (group, user))


def user_ensure(group, user):
    """Ensure that a given user is a member of a given group."""
    d = check(group)
    if user not in d["members"]:
        user_add(group, user)


def user_del(group, user):
        """Remove the given user from the given group."""
        assert check(group), "Group does not exist: %s" % (group)
        if user_check(group, user):
            group_for_user = run(("cat /etc/group | egrep -v '^%s:' | grep "
                                  "'%s' | awk -F':' '{print $1}' | grep -v "
                                  "%s; true") \
                                          % (group, user, user)).splitlines()
            if group_for_user:
                sudo("usermod -G '%s' '%s'" \
                        % (",".join(group_for_user), user))
