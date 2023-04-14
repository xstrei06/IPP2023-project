import argparse
import sys
import os


class ArgumentParser(argparse.ArgumentParser):
    def __init__(self):
        super().__init__(usage='interpret.py [--help] [--source=file] [--input=file]',
                         add_help=False, formatter_class=argparse.RawTextHelpFormatter)
        self.args = None
        self.source = None
        self.input = None
        self.stats_file = None
        self.stats = []
        self.in_opened = False
        self.src_opened = False

    def set_parser(self):
        self.add_argument('--help', action="store_true",
                          help='Display help message and exit (if no other arguments are specified).')
        self.add_argument("--source", metavar="file", type=self.__valid_file, required=False,
                          help="XML file to be interpreted (if not specified, reads from stdin)")
        self.add_argument("--input", metavar="file", type=self.__valid_file, required=False,
                          help="Program input file (if not specified, reads from stdin)")
        self.add_argument("--stats", metavar="file", required=False,
                          help="File to write statistics to")
        self.add_argument("--insts", action="store_true", required=False,
                          help="Writes number of executed instructions to stats file")
        self.add_argument("--hot", action="store_true", required=False,
                          help="Writes lowest order of most executed instruction to stats file")
        self.add_argument("--vars", action="store_true", required=False,
                          help="Writes number of most accessible variables at one time to stats file")
        self.add_argument("--frequent", action="store_true", required=False,
                          help="Writes most frequent instructions to stats file")
        self.add_argument("--print", metavar='string', required=False,
                          help="Writes passed string to stats file")
        self.add_argument("--eol", action="store_true", required=False,
                          help="Writes end of line to stats file")
        self.epilog = "Note: At least one of the arguments --source=file or --input=file must be specified."

    def parse(self):
        self.args = self.parse_args()
        self.source = self.args.source
        self.input = self.args.input
        self.stats_file = self.args.stats
        self.__set_stats(self.args)
        if self.args.help and len(sys.argv) > 2:
            self.error("Invalid arguments.")
        elif self.args.help:
            self.print_help()
            sys.exit(0)
        if self.input is None and self.source is None:
            self.error("Either source or input has to be specified.")

    def __valid_file(self, filename):
        if not os.path.isfile(filename):
            print(f"{filename} is not a valid file.", file=sys.stderr)
            sys.exit(11)
        return filename

    def read_source(self):
        if not self.src_opened:
            self.src_opened = True
            if self.source is None:
                return sys.stdin.read()
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

    def __set_stats(self, args):
        if args.stats is None and \
                (args.insts or args.hot or args.vars or
                 args.frequent or args.print or args.eol):
            self.error("Error: Invalid argument combination.")
        for arg in sys.argv:
            if arg == "--insts":
                self.stats.append({'arg': 'insts'})
            elif arg == "--hot":
                self.stats.append({'arg': 'hot'})
            elif arg == "--vars":
                self.stats.append({'arg': 'vars'})
            elif arg == "--frequent":
                self.stats.append({'arg': 'frequent'})
            elif arg.startswith("--print"):
                self.stats.append({'arg': 'print', 'value': args.print})
            elif arg == "--eol":
                self.stats.append({'arg': 'eol'})

    def error(self, message):
        self.print_usage(sys.stderr)
        self.exit(10, '%s: error: %s\n' % (self.prog, message))