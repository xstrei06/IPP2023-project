import argparse
import os
import sys
import xml.etree.ElementTree as ET
import re
import numbers

instruction_args = {
    'MOVE': [2, "arg1", "arg2"],
    'CREATEFRAME': [0],
    'PUSHFRAME': [0],
    'POPFRAME': [0],
    'DEFVAR': [1, "arg1"],
    'CALL': [1, "arg1"],
    'RETURN': [0],
    'PUSHS': [1, "arg1"],
    'POPS': [1, "arg1"],
    'ADD': [3, "arg1", "arg2", "arg3"],
    'SUB': [3, "arg1", "arg2", "arg3"],
    'MUL': [3, "arg1", "arg2", "arg3"],
    'IDIV': [3, "arg1", "arg2", "arg3"],
    'LT': [3, "arg1", "arg2", "arg3"],
    'GT': [3, "arg1", "arg2", "arg3"],
    'EQ': [3, "arg1", "arg2", "arg3"],
    'AND': [3, "arg1", "arg2", "arg3"],
    'OR': [3, "arg1", "arg2", "arg3"],
    'NOT': [2, "arg1", "arg2"],
    'INT2CHAR': [2, "arg1", "arg2"],
    'STRI2INT': [3, "arg1", "arg2", "arg3"],
    'READ': [2, "arg1", "arg2"],
    'WRITE': [1, "arg1"],
    'CONCAT': [3, "arg1", "arg2", "arg3"],
    'STRLEN': [2, "arg1", "arg2"],
    'GETCHAR': [3, "arg1", "arg2", "arg3"],
    'SETCHAR': [3, "arg1", "arg2", "arg3"],
    'TYPE': [2, "arg1", "arg2"],
    'LABEL': [1, "arg1"],
    'JUMP': [1, "arg1"],
    'JUMPIFEQ': [3, "arg1", "arg2", "arg3"],
    'JUMPIFNEQ': [3, "arg1", "arg2", "arg3"],
    'EXIT': [1, "arg1"],
    'DPRINT': [1, "arg1"],
    'BREAK': [0],
    'CLEARS': [0],
    'ADDS': [0],
    'SUBS': [0],
    'MULS': [0],
    'IDIVS': [0],
    'LTS': [0],
    'GTS': [0],
    'EQS': [0],
    'ANDS': [0],
    'ORS': [0],
    'NOTS': [0],
    'INT2CHARS': [0],
    'STRI2INTS': [0],
    'JUMPIFEQS': [1, "arg1"],
    'JUMPIFNEQS': [1, "arg1"],
    'INT2FLOAT': [2, "arg1", "arg2"],
    'FLOAT2INT': [2, "arg1", "arg2"],
    'DIV': [3, "arg1", "arg2", "arg3"],
}


class ArgumentParser:
    def __init__(self):
        self.parser = None
        self.args = None
        self.source = None
        self.input = None
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
        self.parser.epilog = "Note: At least one of the arguments --source=file or --input=file must be specified."

    def parse(self):
        self.args = self.parser.parse_args()
        self.source = self.args.source
        self.input = self.args.input
        if self.args.help and len(sys.argv) > 2:
            print("Error: Invalid argument combination.", file=sys.stderr)
            sys.exit(10)
        elif self.args.help:
            self.parser.print_help()
            sys.exit(0)
        elif self.input is None and self.source is None:
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


class XMLParser:
    def __init__(self):
        self.root = None
        self.instructions = []
        self.labels = {}

    def parse_xml(self, xmlsource):
        self.check_root(xmlsource)
        self.check_instructions()
        self.check_args()
        self.check_labels()

    def check_root(self, xmlsource):
        try:
            self.root = ET.fromstring(xmlsource)
        except ET.ParseError:
            sys.exit(31)
        for i in self.root.attrib:
            if i not in ["language", "name", "description"]:
                sys.exit(32)
        if self.root.tag != "program":
            sys.exit(32)
        if self.root.attrib["language"].upper() != "IPPCODE23":
            sys.exit(32)

    def check_instructions(self):
        self.instructions = [i for i in self.root.iter("instruction")]
        if len(self.instructions) != len(self.root):
            sys.exit(32)
        for i in self.instructions:
            if 'order' not in i.attrib or 'opcode' not in i.attrib:
                sys.exit(32)
        try:
            self.instructions.sort(key=lambda x: int(x.attrib["order"]))
        except ValueError:
            sys.exit(32)
        prev_order = 0
        for i in self.instructions:
            if int(i.attrib["order"]) == prev_order:
                sys.exit(32)
            prev_order = int(i.attrib["order"])
            if int(i.attrib["order"]) <= 0:
                sys.exit(32)
        for i in range(len(self.instructions)):
            self.instructions[i].attrib["order"] = i
            self.instructions[i].attrib["opcode"] = self.instructions[i].attrib["opcode"].upper()

    def get_instructions(self):
        return self.instructions

    def check_args(self):
        for instruction in self.instructions:
            try:
                if len(instruction) != instruction_args[instruction.attrib["opcode"]][0]:
                    sys.exit(32)
            except KeyError:
                sys.exit(32)
            for arg in instruction:
                if arg.tag not in instruction_args[instruction.attrib["opcode"]]:
                    sys.exit(32)
                if arg.attrib["type"] == "string":  # parses escape sequences
                    arg.text = re.sub(r'\\(\d{3})', lambda x: chr(
                        int(x.group(1))), arg.text)

    def check_labels(self):
        labels = []
        for instruction in self.instructions:
            if instruction.attrib["opcode"] == "LABEL":
                if instruction[0].attrib["type"] != "label":
                    sys.exit(32)
                self.labels[instruction[0].text] = int(instruction.attrib["order"])
                labels.append(instruction[0].text)
        if len(labels) != len(set(labels)):
            sys.exit(52)


class Nil:
    def __init__(self):
        self.val = 'Nil'


class Frame:
    def __init__(self):
        self.frame = {}

    def add_var(self, var):
        self.frame[var] = None

    def change_var(self, var, value):
        self.frame[var] = value

    def get_var(self, var):
        return self.frame[var]


class Main:
    def __init__(self):
        self.parser = ArgumentParser()
        self.parser.set_parser()
        self.parser.parse()
        source = self.parser.read_source()
        self.input_in = self.parser.read_input()
        self.xml_parser = XMLParser()
        self.xml_parser.parse_xml(source)
        self.instructions = self.__get_instruction_objects()
        self.instruction_count = 0

        self.global_frame = Frame()
        self.temporary_frame = None
        self.frame_stack = [None]
        self.call_stack = [None]
        self.data_stack = []
        self.ins_pointer = -1

    def __get_instruction_objects(self):
        instructions = []
        for instruction in self.xml_parser.get_instructions():
            instructions.append(Instruction(instruction))
        return instructions


class Instruction:
    def __init__(self, instruction):
        self.opcode = instruction.attrib["opcode"]
        self.instruction = instruction
        self.args = {}
        self.order = int(instruction.attrib["order"])
        self.invoke_method = {
            'MOVE': self.__move,
            'CREATEFRAME': self.__createframe,
            'PUSHFRAME': self.__pushframe,
            'POPFRAME': self.__popframe,
            'DEFVAR': self.__defvar,
            'CALL': self.__call,
            'RETURN': self.__return,
            'PUSHS': self.__pushs,
            'POPS': self.__pops,
            'ADD': self.__add,
            'SUB': self.__sub,
            'MUL': self.__mul,
            'IDIV': self.__idiv,
            'LT': self.__lt,
            'GT': self.__gt,
            'EQ': self.__eq,
            'AND': self.__and,
            'OR': self.__or,
            'NOT': self.__not,
            'INT2CHAR': self.__int2char,
            'STRI2INT': self.__stri2int,
            'READ': self.__read,
            'WRITE': self.__write,
            'CONCAT': self.__concat,
            'STRLEN': self.__strlen,
            'GETCHAR': self.__getchar,
            'SETCHAR': self.__setchar,
            'TYPE': self.__type,
            'LABEL': self.__label,
            'JUMP': self.__jump,
            'JUMPIFEQ': self.__jumpifeq,
            'JUMPIFNEQ': self.__jumpifneq,
            'EXIT': self.__exit,
            'DPRINT': self.__dprint,
            'BREAK': self.__break,
            'CLEARS': self.__clears,
            'ADDS': self.__adds,
            'SUBS': self.__subs,
            'MULS': self.__muls,
            'IDIVS': self.__idivs,
            'LTS': self.__lts,
            'GTS': self.__gts,
            'EQS': self.__eqs,
            'ANDS': self.__ands,
            'ORS': self.__ors,
            'NOTS': self.__nots,
            'INT2CHARS': self.__int2chars,
            'STRI2INTS': self.__stri2ints,
            'JUMPIFEQS': self.__jumpifeqs,
            'JUMPIFNEQS': self.__jumpifneqs,
            'INT2FLOAT': self.__int2float,
            'FLOAT2INT': self.__float2int,
            'DIV': self.__div,
        }
        if self.opcode not in self.invoke_method:
            sys.exit(32)

    def __set_args(self, inst, glob_frame, temp_frame, local_frame):
        for i in inst:
            if i.attrib["type"] == "var":
                self.args[i.tag] = {'var': i.text[3:],
                                    'frame': self.__get_frame(i.text, glob_frame, temp_frame, local_frame),
                                    'type': 'var'}
                if self.args[i.tag]['frame'] is None:
                    sys.exit(55)
                if self.args[i.tag]['var'] not in self.args[i.tag]['frame'].frame:
                    self.args[i.tag]['val'] = None
                else:
                    self.args[i.tag]['val'] = self.__get_frame(i.text, glob_frame, temp_frame,
                                                               local_frame).get_var(i.text[3:])
            elif i.attrib["type"] == "int":
                if not i.text.isdigit() and i.text[0] != '-':
                    sys.exit(32)
                self.args[i.tag] = {'val': int(i.text),
                                    'type': 'int'}
            elif i.attrib["type"] == "float":
                try:
                    value = float(i.text)
                except ValueError:
                    try:
                        value = float.fromhex(i.text)
                    except ValueError:
                        sys.exit(32)
                self.args[i.tag] = {'val': value,
                                    'type': 'float'}
            elif i.attrib["type"] == "bool":
                if i.text == "true":
                    self.args[i.tag] = {'val': True,
                                        'type': 'bool'}
                elif i.text == "false":
                    self.args[i.tag] = {'val': False,
                                        'type': 'bool'}
                else:
                    sys.exit(57)
            elif i.attrib["type"] == "string":
                self.args[i.tag] = {'val': i.text,
                                    'type': 'string'}
            elif i.attrib["type"] == "label":
                self.args[i.tag] = {'val': i.text,
                                    'type': 'label'}
            elif i.attrib["type"] == "type":
                self.args[i.tag] = {'val': i.text,
                                    'type': 'type'}
            elif i.attrib["type"] == "nil":
                self.args[i.tag] = {'val': Nil(),
                                    'type': 'nil'}

    def __get_frame(self, var, glob_frame, temp_frame, local_frame):
        if var.startswith("GF@"):
            return glob_frame
        elif var.startswith("TF@"):
            return temp_frame
        elif var.startswith("LF@"):
            return local_frame
        else:
            sys.exit(55)

    # noinspection PyArgumentList
    def execute(self, m):
        self.__set_args(self.instruction, main.global_frame, main.temporary_frame, main.frame_stack[0])
        self.invoke_method[self.opcode](m)

    def __move(self, m):
        self.__check_dest_var()
        self.__check_for_vars()
        self.args['arg1']['frame'].change_var(self.args['arg1']['var'], self.args['arg2']['val'])

    def __createframe(self, m):
        m.temporary_frame = Frame()

    def __pushframe(self, m):
        if m.temporary_frame is None:
            sys.exit(55)
        m.frame_stack.insert(0, m.temporary_frame)
        m.temporary_frame = None

    def __popframe(self, m):
        if m.frame_stack[0] is None:
            sys.exit(55)
        m.temporary_frame = m.frame_stack.pop(0)

    def __defvar(self, m):
        self.__check_dest_var()
        if self.args['arg1']['frame'] is None:
            sys.exit(55)
        self.args['arg1']['frame'].add_var(self.args['arg1']['var'])

    def __call(self, m):
        if self.args['arg1']['val'] not in m.xml_parser.labels:
            sys.exit(52)
        m.call_stack.insert(0, m.ins_pointer)
        m.ins_pointer = m.xml_parser.labels[self.args['arg1']['val']] - 1

    def __return(self, m):
        if m.call_stack[0] is None:
            sys.exit(56)
        m.ins_pointer = m.call_stack.pop(0)

    def __pushs(self, m):
        m.data_stack.insert(0, self.args['arg1'])

    def __pops(self, m):
        self.__check_dest_var()
        self.__check_for_vars()
        if not m.data_stack:
            sys.exit(56)
        self.args['arg1']['frame'].change_var(self.args['arg1']['var'], m.data_stack.pop(0)['val'])

    def __add(self, m):
        self.__check_dest_var()
        self.__check_for_vars()
        if (not isinstance(self.args['arg2']['val'], numbers.Number)) or \
                (not isinstance(self.args['arg3']['val'], numbers.Number)):
            sys.exit(53)
        self.args['arg1']['frame'].change_var(self.args['arg1']['var'],
                                              self.args['arg2']['val'] + self.args['arg3']['val'])

    def __sub(self, m):
        self.__check_dest_var()
        self.__check_for_vars()
        if (not isinstance(self.args['arg2']['val'], numbers.Number)) or \
                (not isinstance(self.args['arg3']['val'], numbers.Number)):
            sys.exit(53)
        self.args['arg1']['frame'].change_var(self.args['arg1']['var'],
                                              self.args['arg2']['val'] - self.args['arg3']['val'])

    def __mul(self, m):
        self.__check_dest_var()
        self.__check_for_vars()
        if (not isinstance(self.args['arg2']['val'], numbers.Number)) or \
                (not isinstance(self.args['arg3']['val'], numbers.Number)):
            sys.exit(53)
        self.args['arg1']['frame'].change_var(self.args['arg1']['var'],
                                              self.args['arg2']['val'] * self.args['arg3']['val'])

    def __idiv(self, m):
        self.__check_dest_var()
        self.__check_for_vars()
        if type(self.args['arg2']['val']) != int or type(self.args['arg3']['val']) != int:
            sys.exit(53)
        if self.args['arg3']['val'] == 0:
            sys.exit(57)
        try:
            self.args['arg1']['frame'].change_var(self.args['arg1']['var'],
                                                  self.args['arg2']['val'] // self.args['arg3']['val'])
        except ZeroDivisionError:
            sys.exit(57)

    def __lt(self, m):
        self.__check_dest_var()
        self.__check_for_vars()
        if not (isinstance(self.args['arg2']['val'], type(self.args['arg3']['val']))
                and isinstance(self.args['arg3']['val'], type(self.args['arg2']['val']))):
            sys.exit(53)
        if type(self.args['arg2']['val']) is Nil or type(self.args['arg3']['val']) is Nil:
            sys.exit(53)
        else:
            if self.args['arg2']['val'] < self.args['arg3']['val']:
                self.args['arg1']['frame'].change_var(self.args['arg1']['var'], True)
            else:
                self.args['arg1']['frame'].change_var(self.args['arg1']['var'], False)

    def __gt(self, m):
        self.__check_dest_var()
        self.__check_for_vars()
        if not (isinstance(self.args['arg2']['val'], type(self.args['arg3']['val']))
                and isinstance(self.args['arg3']['val'], type(self.args['arg2']['val']))):
            sys.exit(53)
        if type(self.args['arg2']['val']) is Nil or type(self.args['arg3']['val']) is Nil:
            sys.exit(53)
        else:
            if self.args['arg2']['val'] > self.args['arg3']['val']:
                self.args['arg1']['frame'].change_var(self.args['arg1']['var'], True)
            else:
                self.args['arg1']['frame'].change_var(self.args['arg1']['var'], False)

    def __eq(self, m):
        self.__check_dest_var()
        self.__check_for_vars()
        if not (isinstance(self.args['arg2']['val'], type(self.args['arg3']['val']))
                and isinstance(self.args['arg3']['val'], type(self.args['arg2']['val']))) \
                and (type(self.args['arg2']['val']) is not Nil and type(self.args['arg3']['val']) is not Nil):
            sys.exit(53)
        else:
            if self.args['arg2']['val'] == self.args['arg3']['val']:
                self.args['arg1']['frame'].change_var(self.args['arg1']['var'], True)
            elif type(self.args['arg2']['val']) is Nil and type(self.args['arg3']['val']) is Nil:
                self.args['arg1']['frame'].change_var(self.args['arg1']['var'], True)
            else:
                self.args['arg1']['frame'].change_var(self.args['arg1']['var'], False)

    def __and(self, m):
        self.__check_dest_var()
        self.__check_for_vars()
        if self.args['arg2']['type'] != 'bool' or self.args['arg3']['val'] != 'bool':
            sys.exit(53)
        else:
            if self.args['arg2']['val'] is True and self.args['arg3']['val'] is True:
                self.args['arg1']['frame'].change_var(self.args['arg1']['var'], True)
            else:
                self.args['arg1']['frame'].change_var(self.args['arg1']['var'], False)

    def __or(self, m):
        self.__check_dest_var()
        self.__check_for_vars()
        if self.args['arg2']['type'] != 'bool' or self.args['arg3']['val'] != 'bool':
            sys.exit(53)
        else:
            if self.args['arg2']['val'] is True or self.args['arg3']['val'] is True:
                self.args['arg1']['frame'].change_var(self.args['arg1']['var'], True)
            else:
                self.args['arg1']['frame'].change_var(self.args['arg1']['var'], False)

    def __not(self, m):
        self.__check_dest_var()
        self.__check_for_vars()
        if self.args['arg2']['type'] != 'bool':
            sys.exit(53)
        else:
            if self.args['arg2']['val'] is True:
                self.args['arg1']['frame'].change_var(self.args['arg1']['var'], False)
            else:
                self.args['arg1']['frame'].change_var(self.args['arg1']['var'], True)

    def __int2char(self, m):
        self.__check_dest_var()
        self.__check_for_vars()
        try:
            self.args['arg1']['frame'].change_var(self.args['arg1']['var'], chr(self.args['arg2']['val']))
        except ValueError:
            sys.exit(58)
        except TypeError:
            sys.exit(53)

    def __stri2int(self, m):
        self.__check_dest_var()
        self.__check_for_vars()
        try:
            self.args['arg1']['frame'].change_var(self.args['arg1']['var'],
                                                  ord(self.args['arg2']['val'][self.args['arg3']['val']]))
        except ValueError:
            sys.exit(58)
        except TypeError:
            sys.exit(53)

    def __read(self, m):
        self.__check_dest_var()
        self.__check_for_vars()
        pass
        if m.input_in == 'stdin':
            try:
                if self.args['arg2']['val'] == 'int':
                    self.args['arg1']['frame'].change_var(self.args['arg1']['var'], int(input()))
                elif self.args['arg2']['val'] == 'bool':
                    text = input()
                    if text == 'true':
                        self.args['arg1']['frame'].change_var(self.args['arg1']['var'], True)
                    else:
                        self.args['arg1']['frame'].change_var(self.args['arg1']['var'], False)
                elif self.args['arg2']['val'] == 'string':
                    self.args['arg1']['frame'].change_var(self.args['arg1']['var'], input())
                elif self.args['arg2']['val'] == 'float':
                    value = input()
                    self.args['arg1']['frame'].change_var(self.args['arg1']['var'],
                                                          float.fromhex(value) if value.startswith('0x')
                                                          else float(value))
                else:
                    sys.exit(57)
            except EOFError:
                self.args['arg1']['frame'].change_var(self.args['arg1']['var'], Nil())
        else:
            try:
                if self.args['arg2']['val'] == 'int':
                    self.args['arg1']['frame'].change_var(self.args['arg1']['var'], int(m.input_in[0]))
                    m.input_in.pop(0)
                elif self.args['arg2']['val'] == 'bool':
                    text = m.input_in[0]
                    m.input_in.pop(0)
                    if text == 'true':
                        self.args['arg1']['frame'].change_var(self.args['arg1']['var'], True)
                    else:
                        self.args['arg1']['frame'].change_var(self.args['arg1']['var'], False)
                elif self.args['arg2']['val'] == 'string':
                    self.args['arg1']['frame'].change_var(self.args['arg1']['var'], m.input_in[0])
                    m.input_in.pop(0)
                elif self.args['arg2']['val'] == 'float':
                    value = m.input_in[0]
                    try:
                        value = float(value)
                    except ValueError:
                        try:
                            value = float.fromhex(value)
                        except ValueError:
                            self.args['arg1']['frame'].change_var(self.args['arg1']['var'], None)
                    self.args['arg1']['frame'].change_var(self.args['arg1']['var'], value)
                else:
                    sys.exit(57)
            except EOFError:
                self.args['arg1']['frame'].change_var(self.args['arg1']['var'], Nil())
            except IndexError:
                self.args['arg1']['frame'].change_var(self.args['arg1']['var'], Nil())

    def __write(self, m):
        self.__check_for_vars()
        if type(self.args['arg1']['val']) is Nil:
            print("", end="")
        elif self.args['arg1']['val'] is None:
            sys.exit(56)
        elif self.args['arg1']['val'] is True:
            print("true", end="")
        elif self.args['arg1']['val'] is False:
            print("false", end="")
        elif type(self.args['arg1']['val']) == float:
            print(float.hex(self.args['arg1']['val']), end="")
        else:
            print(self.args['arg1']['val'], end="")

    def __concat(self, m):
        self.__check_dest_var()
        self.__check_for_vars()
        if type(self.args['arg2']['val']) != str or type(self.args['arg3']['val']) != str:
            sys.exit(53)
        else:
            self.args['arg1']['frame'].change_var(self.args['arg1']['var'],
                                                  self.args['arg2']['val'] + self.args['arg3']['val'])

    def __strlen(self, m):
        self.__check_dest_var()
        self.__check_for_vars()
        if type(self.args['arg2']['val']) != str or self.args['arg2']['type'] != 'string':
            sys.exit(53)
        else:
            self.args['arg1']['frame'].change_var(self.args['arg1']['var'], len(self.args['arg2']['val']))

    def __getchar(self, m):
        self.__check_dest_var()
        self.__check_for_vars()
        if self.args['arg3']['val'] is True or self.args['arg3']['val'] is False:
            sys.exit(53)
        try:
            self.args['arg1']['frame'].change_var(self.args['arg1']['var'],
                                                  self.args['arg2']['val'][self.args['arg3']['val']])
        except IndexError:
            sys.exit(58)
        except TypeError:
            sys.exit(53)

    def __setchar(self, m):
        self.__check_dest_var()
        self.__check_for_vars()
        if self.args['arg2']['val'] is True or self.args['arg2']['val'] is False:
            sys.exit(53)
        try:
            if self.args['arg2']['val'] >= len(self.args['arg3']['val']) or self.args['arg2']['val'] < 0:
                sys.exit(58)
            first = self.args['arg1']['val'][:self.args['arg2']['val']]
            second = self.args['arg1']['val'][self.args['arg2']['val'] + 1:]
            self.args['arg1']['frame'].change_var(self.args['arg1']['var'],
                                                  first + self.args['arg3']['val'][0] + second)
        except TypeError:
            sys.exit(53)

    def __type(self, m):
        self.__check_dest_var()
        self.__check_for_vars()
        if self.args['arg2']['type'] == 'int':
            self.args['arg1']['frame'].change_var(self.args['arg1']['var'], 'int')
        elif self.args['arg2']['type'] == 'bool':
            self.args['arg1']['frame'].change_var(self.args['arg1']['var'], 'bool')
        elif self.args['arg2']['type'] == 'string':
            self.args['arg1']['frame'].change_var(self.args['arg1']['var'], 'string')
        elif self.args['arg2']['type'] == 'nil':
            self.args['arg1']['frame'].change_var(self.args['arg1']['var'], Nil())
        elif self.args['arg2']['type'] == 'var' and self.args['arg2']['val'] is None:
            self.args['arg1']['frame'].change_var(self.args['arg1']['var'], '')
        elif self.args['arg2']['type'] == 'var':
            if type(self.args['arg2']['val']) == int:
                self.args['arg1']['frame'].change_var(self.args['arg1']['var'], 'int')
            elif type(self.args['arg2']['val']) == str:
                if self.args['arg2']['val'] is True or self.args['arg2']['val'] is False:
                    self.args['arg1']['frame'].change_var(self.args['arg1']['var'], 'bool')
                else:
                    self.args['arg1']['frame'].change_var(self.args['arg1']['var'], 'string')
        else:
            sys.exit(53)

    def __label(self, m):
        pass

    def __jump(self, m):
        if self.args['arg1']['val'] not in m.xml_parser.labels:
            sys.exit(52)
        m.ins_pointer = m.xml_parser.labels[self.args['arg1']['val']] - 1

    def __jumpifeq(self, m):
        self.__check_for_vars()
        if self.args['arg1']['val'] not in m.xml_parser.labels:
            sys.exit(52)
        if isinstance(self.args['arg2']['val'], type(self.args['arg3']['val']))\
                and isinstance(self.args['arg3']['val'], type(self.args['arg2']['val'])):
            if self.args['arg2']['val'] == self.args['arg3']['val']:
                m.ins_pointer = m.xml_parser.labels[self.args['arg1']['val']] - 1
            elif type(self.args['arg2']['val']) is Nil and type(self.args['arg3']['val']) is Nil:
                m.ins_pointer = m.xml_parser.labels[self.args['arg1']['val']] - 1

    def __jumpifneq(self, m):
        self.__check_for_vars()
        if self.args['arg1']['val'] not in m.xml_parser.labels:
            sys.exit(52)
        if isinstance(self.args['arg2']['val'], type(self.args['arg3']['val'])) \
                and isinstance(self.args['arg3']['val'], type(self.args['arg2']['val'])):
            if type(self.args['arg2']['val']) is Nil and type(self.args['arg3']['val']) is Nil:
                pass
            elif self.args['arg1']['val'] != self.args['arg2']['val']:
                m.ins_pointer = m.xml_parser.labels[self.args['arg1']['val']] - 1

    def __exit(self, m):
        if type(self.args['arg1']['val']) != int:
            sys.exit(53)
        elif self.args['arg1']['val'] < 0 or self.args['arg1']['val'] > 49:
            sys.exit(57)
        else:
            sys.exit(self.args['arg1']['val'])

    def __dprint(self, m):
        print(str(self.args['arg1']['val']), file=sys.stderr)

    def __break(self, m):
        print(f"Pozice vykonavane instrukce: {m.ins_pointer}", file=sys.stderr)
        print(f"Zasobnik volani: {m.call_stack}", file=sys.stderr)
        print(f"Zasobnik ramcu: {m.frame_stack}", file=sys.stderr)
        print(f"Zasobnik dat: {m.data_stack}", file=sys.stderr)
        print(f"Obsah lokalniho ramce: {m.frame_stack[0].frame}", file=sys.stderr)
        print(f"Obsah docasneho ramce: {m.temporary_frame.frame}", file=sys.stderr)
        print(f"Obsah globalniho ramce: {m.global_frame.frame}", file=sys.stderr)
        print(f"Pocet vykonanych instrukci: {m.instruction_count}", file=sys.stderr)

    def __clears(self, m):
        m.data_stack.clear()

    def __adds(self, m):
        self.__check_stack_two_operands(m)
        self.__check_for_vars()
        if type(self.args['arg2']['val']) != int or type(self.args['arg3']['val']) != int:
            sys.exit(53)
        m.data_stack.insert(0, {'type': 'int', 'val': self.args['arg2']['val'] + self.args['arg3']['val']})

    def __subs(self, m):
        self.__check_stack_two_operands(m)
        self.__check_for_vars()
        if type(self.args['arg2']['val']) != int or type(self.args['arg3']['val']) != int:
            sys.exit(53)
        m.data_stack.insert(0, {'type': 'int', 'val': self.args['arg2']['val'] - self.args['arg3']['val']})

    def __muls(self, m):
        self.__check_stack_two_operands(m)
        self.__check_for_vars()
        if type(self.args['arg2']['val']) != int or type(self.args['arg3']['val']) != int:
            sys.exit(53)
        m.data_stack.insert(0, {'type': 'int', 'val': self.args['arg2']['val'] * self.args['arg3']['val']})

    def __idivs(self, m):
        self.__check_stack_two_operands(m)
        self.__check_for_vars()
        if type(self.args['arg2']['val']) != int or type(self.args['arg3']['val']) != int:
            sys.exit(53)
        if self.args['arg3']['val'] == 0:
            sys.exit(57)
        m.data_stack.insert(0, {'type': 'int', 'val': self.args['arg2']['val'] // self.args['arg3']['val']})

    def __lts(self, m):
        self.__check_stack_two_operands(m)
        self.__check_for_vars()
        if not (isinstance(self.args['arg2']['val'], type(self.args['arg3']['val']))
                and isinstance(self.args['arg3']['val'], type(self.args['arg2']['val']))):
            sys.exit(53)
        if type(self.args['arg2']['val']) is Nil or type(self.args['arg3']['val']) is Nil:
            sys.exit(53)
        if self.args['arg2']['val'] < self.args['arg3']['val']:
            m.data_stack.insert(0, {'type': 'bool', 'val': True})
        else:
            m.data_stack.insert(0, {'type': 'bool', 'val': False})

    def __gts(self, m):
        self.__check_stack_two_operands(m)
        self.__check_for_vars()
        if not (isinstance(self.args['arg2']['val'], type(self.args['arg3']['val']))
                and isinstance(self.args['arg3']['val'], type(self.args['arg2']['val']))):
            sys.exit(53)
        if type(self.args['arg2']['val']) is Nil or type(self.args['arg3']['val']) is Nil:
            sys.exit(53)
        if self.args['arg2']['val'] > self.args['arg3']['val']:
            m.data_stack.insert(0, {'type': 'bool', 'val': True})
        else:
            m.data_stack.insert(0, {'type': 'bool', 'val': False})

    def __eqs(self, m):
        self.__check_stack_two_operands(m)
        self.__check_for_vars()
        if not (isinstance(self.args['arg2']['val'], type(self.args['arg3']['val']))
                and isinstance(self.args['arg3']['val'], type(self.args['arg2']['val']))) \
                and (type(self.args['arg2']['val']) is not Nil and type(self.args['arg3']['val']) is not Nil):
            sys.exit(53)
        if self.args['arg2']['val'] == self.args['arg3']['val']:
            m.data_stack.insert(0, {'type': 'bool', 'val': True})
        elif type(self.args['arg2']['val']) is Nil and type(self.args['arg3']['val']) is Nil:
            m.data_stack.insert(0, {'type': 'bool', 'val': True})
        else:
            m.data_stack.insert(0, {'type': 'bool', 'val': False})

    def __ands(self, m):
        self.__check_stack_two_operands(m)
        self.__check_for_vars()
        if not isinstance(self.args['arg2']['val'], bool) or not isinstance(self.args['arg3']['val'], bool):
            sys.exit(53)
        if self.args['arg2']['val'] and self.args['arg3']['val']:
            m.data_stack.insert(0, {'type': 'bool', 'val': True})
        else:
            m.data_stack.insert(0, {'type': 'bool', 'val': False})

    def __ors(self, m):
        self.__check_stack_two_operands(m)
        self.__check_for_vars()
        if not isinstance(self.args['arg2']['val'], bool) or not isinstance(self.args['arg3']['val'], bool):
            sys.exit(53)
        if self.args['arg2']['val'] or self.args['arg3']['val']:
            m.data_stack.insert(0, {'type': 'bool', 'val': True})
        else:
            m.data_stack.insert(0, {'type': 'bool', 'val': False})

    def __nots(self, m):
        self.__check_for_vars()
        if len(m.data_stack) < 1:
            sys.exit(56)
        self.args['arg1'] = m.data_stack.pop()
        if not isinstance(self.args['arg1']['val'], bool):
            sys.exit(53)
        if self.args['arg1']['val']:
            m.data_stack.insert(0, {'type': 'bool', 'val': False})
        else:
            m.data_stack.insert(0, {'type': 'bool', 'val': True})

    def __int2chars(self, m):
        self.__check_for_vars()
        if len(m.data_stack) < 1:
            sys.exit(56)
        self.args['arg1'] = m.data_stack.pop()
        if not isinstance(self.args['arg1']['val'], int):
            sys.exit(53)
        if self.args['arg1']['val'] < 0 or self.args['arg1']['val'] > 1114111:
            sys.exit(58)
        m.data_stack.insert(0, {'type': 'string', 'val': chr(self.args['arg1']['val'])})

    def __stri2ints(self, m):
        self.__check_stack_two_operands(m)
        self.__check_for_vars()
        if not isinstance(self.args['arg2']['val'], str) or not isinstance(self.args['arg3']['val'], int):
            sys.exit(53)
        if self.args['arg3']['val'] < 0 or self.args['arg3']['val'] >= len(self.args['arg2']['val']):
            sys.exit(58)
        m.data_stack.insert(0, {'type': 'int', 'val': ord(self.args['arg2']['val'][self.args['arg3']['val']])})

    def __jumpifeqs(self, m):
        self.__check_stack_two_operands(m)
        self.__check_for_vars()
        if self.args['arg1']['val'] not in m.xml_parser.labels:
            sys.exit(52)
        if not isinstance(self.args['arg2']['val'], type(self.args['arg3']['val'])) \
                and (type(self.args['arg2']['val']) is not Nil and type(self.args['arg3']['val']) is not Nil):
            sys.exit(53)
        if self.args['arg2']['val'] == self.args['arg3']['val']:
            m.ins_pointer = m.xml_parser.labels[self.args['arg1']['val']] - 1
        elif type(self.args['arg2']['val']) is Nil and type(self.args['arg3']['val']) is Nil:
            m.ins_pointer = m.xml_parser.labels[self.args['arg1']['val']] - 1

    def __jumpifneqs(self, m):
        self.__check_stack_two_operands(m)
        self.__check_for_vars()
        if self.args['arg1']['val'] not in m.xml_parser.labels:
            sys.exit(52)
        if not isinstance(self.args['arg2']['val'], type(self.args['arg3']['val'])) \
                and (type(self.args['arg2']['val']) is not Nil and type(self.args['arg3']['val']) is not Nil):
            sys.exit(53)
        if type(self.args['arg2']['val']) is Nil and type(self.args['arg3']['val']) is Nil:
            pass
        elif self.args['arg2']['val'] != self.args['arg3']['val']:
            m.ins_pointer = m.xml_parser.labels[self.args['arg1']['val']] - 1

    def __int2float(self, m):
        self.__check_dest_var()
        self.__check_for_vars()
        if self.args['arg2']['val'] is None:
            sys.exit(56)
        if type(self.args['arg2']['val']) != int:
            sys.exit(53)
        self.args['arg1']['frame'].change_var(self.args['arg1']['var'], float(self.args['arg2']['val']))

    def __float2int(self, m):
        self.__check_dest_var()
        self.__check_for_vars()
        if self.args['arg2']['val'] is None:
            sys.exit(56)
        if type(self.args['arg2']['val']) != float:
            sys.exit(53)
        self.args['arg1']['frame'].change_var(self.args['arg1']['var'], int(self.args['arg2']['val']))

    def __div(self, m):
        self.__check_dest_var()
        self.__check_for_vars()
        if self.args['arg2']['type'] != 'var':
            sys.exit(53)
        if self.args['arg2']['frame'] is None:
            sys.exit(55)
        if self.args['arg2']['var'] not in self.args['arg1']['frame'].frame:
            sys.exit(54)
        if type(self.args['arg2']['val']) != float or type(self.args['arg3']['val']) != float:
            sys.exit(53)
        if self.args['arg3']['val'] == 0:
            sys.exit(57)
        self.args['arg1']['frame'].change_var(self.args['arg1']['var'],
                                              self.args['arg2']['val'] / self.args['arg3']['val'])

    def __check_dest_var(self):
        if self.args['arg1']['type'] != 'var':
            sys.exit(53)

    def __check_for_vars(self):
        for key in self.args:
            if self.args[key]['type'] == 'var':
                if self.args[key]['frame'] is None:
                    sys.exit(55)
                if self.args[key]['var'] not in self.args[key]['frame'].frame:
                    sys.exit(54)

    def __check_stack_two_operands(self, m):
        if len(m.data_stack) < 2:
            sys.exit(56)
        self.args['arg3'] = m.data_stack.pop(0)
        self.args['arg2'] = m.data_stack.pop(0)


if __name__ == "__main__":

    main = Main()

    while True:
        main.ins_pointer += 1
        if main.ins_pointer == len(main.instructions):
            sys.exit(0)
        main.instructions[main.ins_pointer].execute(main)
