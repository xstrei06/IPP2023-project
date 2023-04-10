import argparse
import sys
import os


class ArgumentParser:
    def __init__(self):
        self.parser = None
        self.args = None
        self.source = None
        self.input = None
        self.stats_file = None
        self.stats = []
        self.in_opened = False
        self.src_opened = False

    def set_parser(self):
        self.parser = argparse.ArgumentParser(usage='interpret.py [--help] [--source=file] [--input=file]',
                                              add_help=False, formatter_class=argparse.RawTextHelpFormatter)
        self.parser.add_argument('--help', action="store_true",
                                 help='Display help message and exit (if no other arguments are specified).')
        self.parser.add_argument("--source", metavar="file", type=self.__valid_file, required=False,
                                 help="XML file to be interpreted (if not specified, reads from stdin)")
        self.parser.add_argument("--input", metavar="file", type=self.__valid_file, required=False,
                                 help="Program input file (if not specified, reads from stdin)")
        self.parser.add_argument("--stats", metavar="file", required=False,
                                 help="File to write statistics to")
        self.parser.add_argument("--insts", action="store_true", required=False,
                                 help="Writes number of executed instructions to stats file")
        self.parser.add_argument("--hot", action="store_true", required=False,
                                 help="Writes lowest order of most executed instruction to stats file")
        self.parser.add_argument("--vars", action="store_true", required=False,
                                 help="Writes number of most accessible variables at one time to stats file")
        self.parser.add_argument("--frequent", action="store_true", required=False,
                                 help="Writes most frequent instructions to stats file")
        self.parser.add_argument("--print", metavar='string', required=False,
                                 help="Writes passed string to stats file")
        self.parser.add_argument("--eol", action="store_true", required=False,
                                 help="Writes end of line to stats file")
        self.parser.epilog = "Note: At least one of the arguments --source=file or --input=file must be specified."

    def parse(self):
        self.args = self.parser.parse_args()
        self.source = self.args.source
        self.input = self.args.input
        self.stats_file = self.args.stats
        if self.args.help and len(sys.argv) > 2:
            print("Error: Invalid argument combination.", file=sys.stderr)
            sys.exit(10)
        elif self.args.help:
            self.parser.print_help()
            sys.exit(0)
        if self.input is None and self.source is None:
            print("Either source or input has to be specified.", file=sys.stderr)
            sys.exit(10)

    def __valid_file(self, filename):
        if not os.path.isfile(filename):
            print(f"{filename} is not a valid file.", file=sys.stderr)
            sys.exit(11)
        return filename

    def read_source(self):
        if not self.src_opened:
            self.src_opened = True
            if self.source is None:
                return sys.stdin.readlines()
            src = open(self.source, "r")
            return src.read()
        else:
            return None

    def read_input(self):
        if not self.in_opened:
            self.in_opened = True
            if self.input is None:
                return "stdin"
            inp = open(self.input, "r")
            inp = inp.readlines()
            inp = [i.strip() for i in inp]
            return inp
        else:
            return None
