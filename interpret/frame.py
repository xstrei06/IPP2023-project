import sys


class Frame:
    def __init__(self):
        self.frame = {}

    def add_var(self, var):
        if var in self.frame:
            sys.exit(52)
        self.frame[var] = None

    def change_var(self, var, value):
        if var not in self.frame:
            sys.exit(54)
        self.frame[var] = value

    def get_var(self, var):
        if var not in self.frame:
            sys.exit(54)
        return self.frame[var]
