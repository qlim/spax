import re

def regexFromSearchString(s):
	chars = []
	for c in s:
		if c in r'\.?*+()[]':
			c = r'\%s' % c
		chars.append(c)
	r = r"".join(chars)
	return re.compile(r, re.M)
