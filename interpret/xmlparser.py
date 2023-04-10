import sys
import xml.etree.ElementTree as ET
import re


class XMLParser:
    def __init__(self):
        self.root = None
        self.instructions = []
        self.labels = {}
        self.instruction_args = {
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
            self.instructions[i].attrib["order_orig"] = self.instructions[i].attrib["order"]
            self.instructions[i].attrib["order"] = i
            self.instructions[i].attrib["opcode"] = self.instructions[i].attrib["opcode"].upper()

    def get_instructions(self):
        return self.instructions

    def check_args(self):
        for instruction in self.instructions:
            try:
                if len(instruction) != self.instruction_args[instruction.attrib["opcode"]][0]:
                    sys.exit(32)
            except KeyError:
                sys.exit(32)
            for arg in instruction:
                if arg.tag not in self.instruction_args[instruction.attrib["opcode"]]:
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
