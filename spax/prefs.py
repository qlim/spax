from ConfigParser import SafeConfigParser, NoSectionError, NoOptionError
import os

PREFS_FILE = '.spaxprefs'

class Prefs(object):
    def __init__(self, path=None):
        self.cp = SafeConfigParser()
        self.path = path or os.path.join(os.path.expanduser('~'), PREFS_FILE)
        self.cp.read(self.path)

    def get(self, section, option, default=None):
        try:
            return self.cp.get(section, option)
        except (NoSectionError, NoOptionError):
            return default

    def set(self, section, option, value):
        if not self.cp.has_section(section):
            self.cp.add_section(section)
        self.cp.set(section, option, value)
        self.write()

    def write(self):
        try:
            self.cp.write(open(self.path, 'w'))
        except IOError:
            pass #fail silently for now

prefs = Prefs()