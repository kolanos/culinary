import re
import string

RE_SPACES = re.compile("[\s\t]+")
MAC_EOL = "\n"
UNIX_EOL = "\n"
WINDOWS_EOL = "\r\n"


def detect_eol(text):
    # FIXME: Should look at the first line
    if text.find("\r\n") != -1:
        return WINDOWS_EOL
    elif text.find("\n") != -1:
        return UNIX_EOL
    elif text.find("\r") != -1:
        return MAC_EOL
    else:
        return "\n"


def get_line(text, predicate):
    """Returns the first line that matches the given predicate."""
    for line in text.split("\n"):
        if predicate(line):
            return line
    return ""


def normalize(text):
    """Converts tabs and spaces to single space and strips the text."""
    return RE_SPACES.sub(" ", text).strip()


def nospace(text):
    """Converts tabs and spaces to single space and strips the text."""
    return RE_SPACES.sub("", text).strip()


def replace_line(text, old, new, find=lambda old, new: old == new,
                 process=lambda _: _):
    """Replaces lines equal to 'old' with 'new', returning the new
    text and the count of replacements."""
    res = []
    replaced = 0
    eol = detect_eol(text)
    for line in text.split(eol):
        if find(process(line), process(old)):
            res.append(new)
            replaced += 1
        else:
            res.append(line)
    return eol.join(res), replaced


def ensure_line(text, *lines):
    """Ensures that the given lines are present in the given text,
    otherwise appends the lines that are not already in the text at
    the end of it."""
    eol = detect_eol(text)
    res = list(text.split(eol))
    if res[0] == '' and len(res) == 1:
        res = list()
    for line in lines:
        assert line.find(eol) == -1, \
                "No EOL allowed in lines parameter: " + repr(line)
        found = False
        for l in res:
            if l == line:
                found = True
                break
        if not found:
            res.append(line)
    return eol.join(res)


def strip_margin(text, margin="|"):
    res = []
    eol = detect_eol(text)
    for line in text.split(eol):
        l = line.split(margin, 1)
        if len(l) == 2:
            _, line = l
            res.append(line)
    return eol.join(res)


def template(text, variables):
    """Substitutes '${PLACEHOLDER}'s within the text with the
    corresponding values from variables."""
    template = string.Template(text)
    return template.safe_substitute(variables)
