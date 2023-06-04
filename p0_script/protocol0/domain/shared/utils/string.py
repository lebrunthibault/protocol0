from typing import Any


def smart_string(s):
    # type: (Any) -> str
    return s


def title(s):
    # type: (str) -> str
    # .title is not good because of words starting with numbers
    if not s:
        return s

    s = s.strip()

    return s[0].capitalize() + s[1:]
