import re

def regexFromSearchString(s, flags=re.M):
    chars = []
    for c in s:
        if c in r'\.?*+()[]':
            c = r'\%s' % c
        chars.append(c)
    r = r"".join(chars)
    return re.compile(r, flags)
