import sys


class Statistics:
    def __init__(self, file, args):
        self.stats = []
        self.stats_file = file
        self.__set_stats(args)
        self.frequent = {
            'MOVE': 0,
            'CREATEFRAME': 0,
            'PUSHFRAME': 0,
            'POPFRAME': 0,
            'DEFVAR': 0,
            'CALL': 0,
            'RETURN': 0,
            'PUSHS': 0,
            'POPS': 0,
            'ADD': 0,
            'SUB': 0,
            'MUL': 0,
            'IDIV': 0,
            'LT': 0,
            'GT': 0,
            'EQ': 0,
            'AND': 0,
            'OR': 0,
            'NOT': 0,
            'INT2CHAR': 0,
            'STRI2INT': 0,
            'READ': 0,
            'WRITE': 0,
            'CONCAT': 0,
            'STRLEN': 0,
            'GETCHAR': 0,
            'SETCHAR': 0,
            'TYPE': 0,
            'LABEL': 0,
            'JUMP': 0,
            'JUMPIFEQ': 0,
            'JUMPIFNEQ': 0,
            'EXIT': 0,
            'DPRINT': 0,
            'BREAK': 0,
            'CLEARS': 0,
            'ADDS': 0,
            'SUBS': 0,
            'MULS': 0,
            'IDIVS': 0,
            'LTS': 0,
            'GTS': 0,
            'EQS': 0,
            'ANDS': 0,
            'ORS': 0,
            'NOTS': 0,
            'INT2CHARS': 0,
            'STRI2INTS': 0,
            'JUMPIFEQS': 0,
            'JUMPIFNEQS': 0,
            'INT2FLOAT': 0,
            'FLOAT2INT': 0,
            'DIV': 0,
        }

    def __set_stats(self, args):
        if args.stats is None and \
                (args.insts or args.hot or args.vars or
                 args.frequent or args.print or args.eol):
            print("Error: Invalid argument combination.", file=sys.stderr)
            sys.exit(10)
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

    def print_stats(self, m):
        file = open(self.stats_file, "w")
        for stat in self.stats:
            if stat['arg'] == 'insts':
                print(str(m.insts), file=file, end='')
            elif stat['arg'] == 'hot':
                print(str(m.hot), file=file, end='')
            elif stat['arg'] == 'vars':
                print(str(m.vars), file=file, end='')
            elif stat['arg'] == 'frequent':
                frequent_to_print = []
                max_key = max(self.frequent, key=lambda key: self.frequent[key])
                max_count = self.frequent[max_key]
                for i in sorted(self.frequent, reverse=True):
                    if self.frequent[i] == max_count:
                        frequent_to_print.append(i)
                for i in frequent_to_print:
                    if i != frequent_to_print[-1]:
                        print(i + ',', file=file, end='')
                    else:
                        print(i, file=file, end='')
            elif stat['arg'] == 'print':
                print(stat['value'], file=file, end='')
            elif stat['arg'] == 'eol':
                print(file=file)
        file.close()
