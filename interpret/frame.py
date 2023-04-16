"""
FIT VUT IPP 2023
Projekt 2 - Interpret XML reprezentace jazyka IPPcode23
Autor: Jaroslav Streit (xstrei06)
Soubor: frame.py
"""

import sys


class Frame:
    """Trida pro reprezentaci ramcu programu"""
    def __init__(self):
        self.frame = {}

    def add_var(self, var):
        """Metoda pro pridani nove promenne do ramce (DEFVAR)"""
        if var in self.frame:
            sys.exit(52)
        self.frame[var] = None

    def change_var(self, var, value):
        """Metoda pro zmenu hodnoty promenne"""
        if var not in self.frame:
            sys.exit(54)
        self.frame[var] = value

    def get_var(self, var):
        """Metoda pro ziskani hodnoty promenne"""
        if var not in self.frame:
            sys.exit(54)
        return self.frame[var]
