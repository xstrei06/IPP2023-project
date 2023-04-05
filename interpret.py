import argparse
import os
import sys
import xml.etree.ElementTree as ET
import re
import exceptions as ex


def valid_file(filename):
    if not os.path.isfile(filename):
        sys.stderr.write(f"{filename} is not a valid file")
        sys.exit(11)
    return filename


instruction_args = {
    'MOVE': [2, "arg1", "arg2"],
    'CREATEFRAME': [0],
    'PUSHFRAME': [0],
    'POPFRAME': [0],
    'DEFVAR': [1, "arg1"],
    'CALL': [1, "arg1"],
    'RETURN': [0],
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
    'BREAK': [0]
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
        self.parser.add_argument("--source", metavar="file", type=valid_file, required=False,
                                 help="XML file to be interpreted (if not specified, reads from stdin)")
        self.parser.add_argument("--input", metavar="file", type=valid_file, required=False,
                                 help="Program input file (if not specified, reads from stdin)")
        self.parser.epilog = "Note: At least one of the arguments --source=file or --input=file must be specified."

    def parse(self):
        self.args = self.parser.parse_args()
        self.source = self.args.source
        self.input = self.args.input
        if self.args.help and len(sys.argv) > 2:
            self.parser.error("Invalid argument combination.")
        elif self.args.help:
            self.parser.print_help()
            sys.exit(0)
        elif self.input is None and self.source is None:
            self.parser.error("Either source or input has to be specified.")

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
            return inp.read()
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
        labels = self.root.findall(".//instruction[@opcode='LABEL']")
        if len(labels) != len(set(labels)):
            sys.exit(52)
        for label in labels:
            if label[0].attrib["type"] != "label":
                sys.exit(32)
            self.labels[label[0].text] = int(label.attrib["order"])


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

        self.global_frame = Frame()
        self.temporary_frame = None
        self.frame_stack = [None]
        self.call_stack = [None]
        self.data_stack = [None]
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
            'BREAK': self.__break
        }
        if self.opcode not in self.invoke_method:
            sys.exit(32)

    def __set_args(self, inst, glob_frame, temp_frame, local_frame):
        for i in inst:
            if i.attrib["type"] == "var":
                self.args[i.tag] = {'var': i.text[3:],
                                    'frame': self.__get_frame(i.text, glob_frame, temp_frame, local_frame)}
                if self.args[i.tag]['frame'] is None:
                    sys.exit(55)
                if self.args[i.tag]['var'] not in self.args[i.tag]['frame'].frame:
                    self.args[i.tag]['val'] = None
                else:
                    self.args[i.tag]['val'] = self.__get_frame(i.text, glob_frame, temp_frame,
                                                               local_frame).get_var(i.text[3:])
            elif i.attrib["type"] == "int":
                self.args[i.tag] = {'val': int(i.text)}
            elif i.attrib["type"] == "bool":
                if i.text == "true":
                    self.args[i.tag] = {'val': 'true',
                                        'type': 'bool'}
                elif i.text == "false":
                    self.args[i.tag] = {'val': 'false',
                                        'type': 'bool'}
            elif i.attrib["type"] == "string":
                self.args[i.tag] = {'val': i.text}
            elif i.attrib["type"] == "label":
                self.args[i.tag] = {'val': i.text}
            elif i.attrib["type"] == "type":
                self.args[i.tag] = {'val': i.text}
            elif i.attrib["type"] == "nil":
                self.args[i.tag] = {'val': None}

    def __get_frame(self, var, glob_frame, temp_frame, local_frame):
        if var.startswith("GF@"):
            return glob_frame
        elif var.startswith("TF@"):
            return temp_frame
        elif var.startswith("LF@"):
            return local_frame
        else:
            sys.exit(54)

    def execute(self, main):
        self.__set_args(self.instruction, main.global_frame, main.temporary_frame, main.frame_stack[0])
        self.invoke_method[self.opcode](main)

    def __move(self, main):
        self.args['arg1']['frame'].change_var(self.args['arg1']['var'], self.args['arg2']['val'])

    def __createframe(self, main):
        main.temporary_frame = Frame()

    def __pushframe(self, main):
        main.frame_stack.insert(0, main.temporary_frame)
        main.temporary_frame = None

    def __popframe(self, main):
        main.frame_stack.pop(0)

    def __defvar(self, main):
        self.args['arg1']['frame'].add_var(self.args['arg1']['var'])

    def __call(self, main):
        if self.args['arg1']['val'] not in main.xml_parser.labels:
            sys.exit(52)
        main.call_stack.insert(0, main.ins_pointer)
        main.ins_pointer = main.xml_parser.labels[self.args['arg1']['val']] - 1

    def __return(self, main):
        if main.call_stack[0] is None:
            sys.exit(56)
        main.ins_pointer = main.call_stack.pop(0)

    def __pushs(self, main):
        main.data_stack.insert(0, self.args['arg1']['val'])

    def __pops(self, main):
        self.args['arg1']['frame'].change_var(self.args['arg1']['var'], main.data_stack.pop(0))

    def __add(self, main):
        self.args['arg1']['frame'].change_var(self.args['arg1']['var'],
                                              self.args['arg2']['val'] + self.args['arg3']['val'])

    def __sub(self, main):
        self.args['arg1']['frame'].change_var(self.args['arg1']['var'],
                                              self.args['arg2']['val'] - self.args['arg3']['val'])

    def __mul(self, main):
        self.args['arg1']['frame'].change_var(self.args['arg1']['var'],
                                              self.args['arg2']['val'] * self.args['arg3']['val'])

    def __idiv(self, main):
        if self.args['arg3']['val'] == 0:
            sys.exit(57)
        try:
            self.args['arg1']['frame'].change_var(self.args['arg1']['var'],
                                                  self.args['arg2']['val'] // self.args['arg3']['val'])
        except ZeroDivisionError:
            sys.exit(57)

    def __lt(self, main):
        if type(self.args['arg2']['val']) != type(self.args['arg3']['val']):
            sys.exit(53)
        else:
            if self.args['arg2']['val'] < self.args['arg3']['val']:
                self.args['arg1']['frame'].change_var(self.args['arg1']['var'], 'true')
            else:
                self.args['arg1']['frame'].change_var(self.args['arg1']['var'], 'false')

    def __gt(self, main):
        if type(self.args['arg2']['val']) != type(self.args['arg3']['val']):
            sys.exit(53)
        else:
            if self.args['arg2']['val'] > self.args['arg3']['val']:
                self.args['arg1']['frame'].change_var(self.args['arg1']['var'], 'true')
            else:
                self.args['arg1']['frame'].change_var(self.args['arg1']['var'], 'false')

    def __eq(self, main):
        if type(self.args['arg2']['val']) != type(self.args['arg3']['val']):
            sys.exit(53)
        else:
            if self.args['arg2']['val'] == self.args['arg3']['val']:
                self.args['arg1']['frame'].change_var(self.args['arg1']['var'], 'true')
            else:
                self.args['arg1']['frame'].change_var(self.args['arg1']['var'], 'false')

    def __and(self, main):
        pass

    def __or(self, main):
        pass

    def __not(self, main):
        pass

    def __int2char(self, main):
        pass

    def __stri2int(self, main):
        pass

    def __read(self, main):
        pass

    def __write(self, main):
        if self.args['arg1']['val'] is None:
            print("", end="")
        else:
            print(self.args['arg1']['val'], end="")

    def __concat(self, main):
        pass

    def __strlen(self, main):
        pass

    def __getchar(self, main):
        pass

    def __setchar(self, main):
        pass

    def __type(self, main):
        pass

    def __label(self, main):
        pass

    def __jump(self, main):
        pass

    def __jumpifeq(self, main):
        pass

    def __jumpifneq(self, main):
        pass

    def __exit(self, main):
        pass

    def __dprint(self, main):
        pass

    def __break(self, main):
        pass


if __name__ == "__main__":

    main = Main()

    while True:
        main.ins_pointer += 1
        if main.ins_pointer == len(main.instructions):
            sys.exit(0)
        main.instructions[main.ins_pointer].execute(main)
