from fabric.context_managers import cd, hide, lcd, settings
from fabric.utils import puts

from . import mode
from .core import sudo


def database_check(name):
    cmd = "psql -U postgres -l | grep '\ {0}  *|'".format(name)
    with settings(hide('everything'), warn_only=True):
        return bool(run_as_postgres(cmd))


def database_create(database_name, tablespace=None, locale=None, encoding=None,
                    owner=None, template=None):
    opts = [
        tablespace and '--tablespace={0}'.format(tablespace),
        locale and '--locale={0}'.format(locale),
        encoding and '--encoding={0}'.format(encoding),
        owner and '--owner={0}'.format(owner),
        template and '--template={0}'.format(template),
    ]
    cmd = 'createdb -U postgres {opts} {database_name}'.format(
        opts=' '.join(opt for opt in opts if opt is not None),
        database_name=database_name,
    )
    run_as_postgres(cmd)


def database_ensure(database_name, tablespace=None, locale=None, encoding=None,
                    owner=None, template=None):
    if database_check(database_name):
        puts("Database '{0}' exists.".format(database_name))
    else:
        puts("Database '{0}' doesn't exist. Creating...".format(database_name))
        database_create(database_name, tablespace, locale, encoding, owner,
                        template)


def role_check(username):
    cmd = "psql -U postgres -c '\\du' | grep '^  *{0}  *|'".format(username)
    with settings(hide('everything'), warn_only=True):
        return bool(run_as_postgres(cmd))


def role_create(username, password, superuser=False, createdb=False,
                createrole=False, inherit=True, login=True):
    opts = [
        'SUPERUSER' if superuser else 'NOSUPERUSER',
        'CREATEDB' if createdb else 'NOCREATEDB',
        'CREATEROLE' if createrole else 'NOCREATEROLE',
        'INHERIT' if inherit else 'NOINHERIT',
        'LOGIN' if login else 'NOLOGIN'
    ]
    sql = "CREATE ROLE {username} WITH {opts} PASSWORD '{password}'"
    sql = sql.format(username=username, opts=' '.join(opts), password=password)
    cmd = 'psql -U postgres -c "{0}"'.format(sql)
    run_as_postgres(cmd)


def role_ensure(username, password, superuser=False, createdb=False,
                createrole=False, inherit=True, login=True):
    if role_check(username):
        puts("Role '{0}' exists.".format(username))
    else:
        puts("Role '{0}' doesn't exist. Creating...".format(username))
        role_create(username, password, superuser, createdb, createrole,
                    inherit, login)


def run_as_postgres(cmd):
    """Run given command as postgres user."""
    # The cd below is needed to avoid the following warning:
    #
    #     could not change directory to "/root"
    #
    d = lcd if mode.is_local() else cd
    with d('/'):
        return sudo(cmd, user='postgres')
