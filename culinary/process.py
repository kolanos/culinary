from .core import run
from .text import RE_SPACES

# =============================================================================
#
# PROCESS OPERATIONS
#
# =============================================================================


def find(name, exact=False):
    """
    Returns the pids of processes with the given name. If exact is `False` it
    will return the list of all processes that start with the given `name`.
    """
    processes = run("ps aux | grep {0}".format(name))
    res = []
    for line in processes.split("\n"):
        if not line.strip():
            continue
        line = RE_SPACES.split(line, 10)
        # We skip lines that are not like we expect them (sometimes error
        # message creep up the output)
        if len(line) < 11:
            continue
        user, pid, cpu, mem, vsz, rss, tty, stat, start, time, command = line
        if (exact and command == name) \
                or (not exact and command.startswith(name)):
            res.append(pid)
    return res


def kill(name, signal=9, exact=False):
    """
    Kills the given processes with the given name. If exact is `False` it will
    return the list of all processes that start with the given `name`.
"""
    for pid in find(name, exact):
        run("kill -s {0} {1}".format(signal, pid))
