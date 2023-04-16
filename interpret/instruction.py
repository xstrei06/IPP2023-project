"""
FIT VUT IPP 2023
Projekt 2 - Interpret XML reprezentace jazyka IPPcode23
Autor: Jaroslav Streit (xstrei06)
Soubor: instruction.py
"""

import sys
import re
from frame import Frame
from nil_type import Nil


class Instruction:
    def __init__(self, instruction):
        self.opcode = instruction.attrib["opcode"]
        self.instruction = instruction
        self.args = {}
        self.order = int(instruction.attrib["order"])
        self.order_orig = int(instruction.attrib["order_orig"])
        self.invoke_method = {  # slovnik pro volani odpovidajici metody podle opcode instrukce
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
        self.hot = 0

    def __set_args(self, inst, glob_frame, temp_frame, local_frame) -> None:
        """Metoda pro nastaveni argumentu instrukce"""
        for i in inst:
            if i.attrib["type"] == "var":
                if re.match(r'^(LF|GF|TF)@[a-zA-Z_$&%*!?-][a-zA-Z_$&%*!?0-9-]*$', i.text) is None:
                    sys.exit(32)
                self.args[i.tag] = {'var': i.text[3:],
                                    'frame': self.__get_frame(i.text, glob_frame, temp_frame, local_frame),
                                    'type': 'var'}
                self.__check_var(i.tag)
                if self.opcode == 'DEFVAR':
                    self.args[i.tag]['val'] = None
                else:
                    self.args[i.tag]['val'] = self.__get_frame(i.text, glob_frame, temp_frame,
                                                               local_frame).get_var(i.text[3:])
                    if i.tag == 'arg1' and self.args[i.tag]['val'] is None and \
                            (self.opcode == 'PUSHS' or self.opcode == 'WRITE' or
                             self.opcode == 'DPRINT' or self.opcode == 'EXIT'):
                        sys.exit(56)
                    elif i.tag != 'arg1' and self.args[i.tag]['val'] is None and self.opcode != 'TYPE':
                        sys.exit(56)
            elif i.attrib["type"] == "int":
                try:
                    self.args[i.tag] = {'val': int(i.text, 0), 'type': 'int'}
                except ValueError:
                    sys.exit(32)
            elif i.attrib["type"] == "float":
                try:
                    self.args[i.tag] = {'val': float(i.text), 'type': 'float'}
                except ValueError:
                    try:
                        self.args[i.tag] = {'val': float.fromhex(i.text), 'type': 'float'}
                    except ValueError:
                        sys.exit(32)
            elif i.attrib["type"] == "bool":
                if i.text == "true":
                    self.args[i.tag] = {'val': True, 'type': 'bool'}
                elif i.text == "false":
                    self.args[i.tag] = {'val': False, 'type': 'bool'}
                else:
                    sys.exit(32)
            elif i.attrib["type"] == "string":
                self.args[i.tag] = {'val': i.text, 'type': 'string'}
            elif i.attrib["type"] == "label":
                if re.match('^[a-zA-Z_$&%*!?-][a-zA-Z_$&%*!?0-9-]*$', i.text) is None:
                    sys.exit(32)
                self.args[i.tag] = {'val': i.text, 'type': 'label'}
            elif i.attrib["type"] == "type":
                if re.match('^(int|float|string|bool|nil)$', i.text) is None:
                    sys.exit(32)
                self.args[i.tag] = {'val': i.text, 'type': 'type'}
            elif i.attrib["type"] == "nil":
                if i.text != "nil":
                    sys.exit(32)
                self.args[i.tag] = {'val': Nil(), 'type': 'nil'}
            else:
                sys.exit(32)

    def __get_frame(self, var, glob_frame, temp_frame, local_frame) -> Frame:
        """Metoda pro ziskani ramce promenne"""
        if var.startswith("GF@"):
            return glob_frame
        elif var.startswith("TF@"):
            return temp_frame
        elif var.startswith("LF@"):
            return local_frame
        else:
            sys.exit(32)

    def execute(self, m) -> None:
        """Metoda pro provedeni instrukce
        Metoda take sbira nektere statistiky"""
        self.__set_args(self.instruction, m.global_frame, m.temporary_frame, m.frame_stack[0])
        self.invoke_method[self.opcode](m)
        if self.opcode != "LABEL" and self.opcode != 'BREAK' and self.opcode != 'DPRINT':
            m.insts += 1
        self.hot += 1
        if self.hot > m.hot:
            m.hot = self.hot
            m.hot_order = self.order_orig
        elif self.hot == m.hot:
            if self.order_orig < m.hot_order:
                m.hot_order = self.order_orig
        m.stats.frequent[self.opcode] += 1

    """Nasleduji metody pro provedeni jednotlivych instrukci"""
    """Zakladni instrukce"""
    def __move(self, m) -> None:
        self.__check_dest_var()
        self.args['arg1']['frame'].change_var(self.args['arg1']['var'], self.args['arg2']['val'])

    def __createframe(self, m) -> None:
        m.temporary_frame = Frame()

    def __pushframe(self, m) -> None:
        if m.temporary_frame is None:
            sys.exit(55)
        m.frame_stack.insert(0, m.temporary_frame)
        m.temporary_frame = None

    def __popframe(self, m) -> None:
        if m.frame_stack[0] is None:
            sys.exit(55)
        m.temporary_frame = m.frame_stack.pop(0)
        m.count_available_vars()

    def __defvar(self, m) -> None:
        self.__check_dest_var()
        if self.args['arg1']['frame'] is None:
            sys.exit(55)
        self.args['arg1']['frame'].add_var(self.args['arg1']['var'])
        m.count_available_vars()

    def __call(self, m) -> None:
        if self.args['arg1']['val'] not in m.xml_parser.labels:
            sys.exit(52)
        m.call_stack.insert(0, m.ins_pointer)
        m.ins_pointer = m.xml_parser.labels[self.args['arg1']['val']] - 1

    def __return(self, m) -> None:
        if m.call_stack[0] is None:
            sys.exit(56)
        m.ins_pointer = m.call_stack.pop(0)

    def __pushs(self, m) -> None:
        m.data_stack.insert(0, self.args['arg1'])

    def __pops(self, m) -> None:
        self.__check_dest_var()
        if not m.data_stack:
            sys.exit(56)
        self.args['arg1']['frame'].change_var(self.args['arg1']['var'], m.data_stack.pop(0)['val'])

    def __add(self, m) -> None:
        self.__check_dest_var()
        if not ((type(self.args['arg2']['val']) == int and type(self.args['arg3']['val']) == int) or
                (type(self.args['arg2']['val']) == float and type(self.args['arg3']['val']) == float)):
            sys.exit(53)
        self.args['arg1']['frame'].change_var(self.args['arg1']['var'],
                                              self.args['arg2']['val'] + self.args['arg3']['val'])

    def __sub(self, m) -> None:
        self.__check_dest_var()
        if not ((type(self.args['arg2']['val']) == int and type(self.args['arg3']['val']) == int) or
                (type(self.args['arg2']['val']) == float and type(self.args['arg3']['val']) == float)):
            sys.exit(53)
        self.args['arg1']['frame'].change_var(self.args['arg1']['var'],
                                              self.args['arg2']['val'] - self.args['arg3']['val'])

    def __mul(self, m) -> None:
        self.__check_dest_var()
        if not ((type(self.args['arg2']['val']) == int and type(self.args['arg3']['val']) == int) or
                (type(self.args['arg2']['val']) == float and type(self.args['arg3']['val']) == float)):
            sys.exit(53)
        self.args['arg1']['frame'].change_var(self.args['arg1']['var'],
                                              self.args['arg2']['val'] * self.args['arg3']['val'])

    def __idiv(self, m) -> None:
        self.__check_dest_var()
        if type(self.args['arg2']['val']) != int or type(self.args['arg3']['val']) != int:
            sys.exit(53)
        if self.args['arg3']['val'] == 0:
            sys.exit(57)
        self.args['arg1']['frame'].change_var(self.args['arg1']['var'],
                                                  self.args['arg2']['val'] // self.args['arg3']['val'])

    def __lt(self, m) -> None:
        self.__check_dest_var()
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

    def __gt(self, m) -> None:
        self.__check_dest_var()
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

    def __eq(self, m) -> None:
        self.__check_dest_var()
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

    def __and(self, m) -> None:
        self.__check_dest_var()
        if type(self.args['arg2']['val']) != bool or type(self.args['arg3']['val']) != bool:
            sys.exit(53)
        else:
            if self.args['arg2']['val'] is True and self.args['arg3']['val'] is True:
                self.args['arg1']['frame'].change_var(self.args['arg1']['var'], True)
            else:
                self.args['arg1']['frame'].change_var(self.args['arg1']['var'], False)

    def __or(self, m) -> None:
        self.__check_dest_var()
        if type(self.args['arg2']['val']) != bool or type(self.args['arg3']['val']) != bool:
            sys.exit(53)
        else:
            if self.args['arg2']['val'] is True or self.args['arg3']['val'] is True:
                self.args['arg1']['frame'].change_var(self.args['arg1']['var'], True)
            else:
                self.args['arg1']['frame'].change_var(self.args['arg1']['var'], False)

    def __not(self, m) -> None:
        self.__check_dest_var()
        if type(self.args['arg2']['val']) != bool:
            sys.exit(53)
        else:
            if self.args['arg2']['val'] is True:
                self.args['arg1']['frame'].change_var(self.args['arg1']['var'], False)
            else:
                self.args['arg1']['frame'].change_var(self.args['arg1']['var'], True)

    def __int2char(self, m) -> None:
        self.__check_dest_var()
        if type(self.args['arg2']['val']) != int:
            sys.exit(53)
        if self.args['arg2']['val'] < 0 or self.args['arg2']['val'] > 1114111:
            sys.exit(58)
        self.args['arg1']['frame'].change_var(self.args['arg1']['var'], chr(self.args['arg2']['val']))

    def __stri2int(self, m) -> None:
        self.__check_dest_var()
        if type(self.args['arg2']['val']) != str or type(self.args['arg3']['val']) != int:
            sys.exit(53)
        if self.args['arg3']['val'] < 0 or self.args['arg3']['val'] >= len(self.args['arg2']['val']):
            sys.exit(58)
        self.args['arg1']['frame'].change_var(self.args['arg1']['var'],
                                              ord(self.args['arg2']['val'][self.args['arg3']['val']]))

    def __read(self, m) -> None:
        self.__check_dest_var()
        if self.args['arg2']['val'] not in ['int', 'bool', 'string', 'float']:
            sys.exit(32)
        if m.input_in == 'stdin':  # nacitani ze standardniho vstupu
            try:
                read_in = input()
                if read_in == '':
                    self.args['arg1']['frame'].change_var(self.args['arg1']['var'], Nil())
                else:
                    if self.args['arg2']['val'] == 'int':
                        try:
                            self.args['arg1']['frame'].change_var(self.args['arg1']['var'], int(read_in, 0))
                        except ValueError:
                            self.args['arg1']['frame'].change_var(self.args['arg1']['var'], Nil())
                    elif self.args['arg2']['val'] == 'bool':
                        text = input()
                        if text.lower() == 'true':
                            self.args['arg1']['frame'].change_var(self.args['arg1']['var'], True)
                        else:
                            self.args['arg1']['frame'].change_var(self.args['arg1']['var'], False)
                    elif self.args['arg2']['val'] == 'string':
                        self.args['arg1']['frame'].change_var(self.args['arg1']['var'], read_in)
                    elif self.args['arg2']['val'] == 'float':
                        try:
                            self.args['arg1']['frame'].change_var(self.args['arg1']['var'], float(read_in))
                        except ValueError:
                            try:
                                self.args['arg1']['frame'].change_var(self.args['arg1']['var'], float.fromhex(read_in))
                            except ValueError:
                                self.args['arg1']['frame'].change_var(self.args['arg1']['var'], Nil())
                    else:
                        sys.exit(32)
            except EOFError:
                self.args['arg1']['frame'].change_var(self.args['arg1']['var'], Nil())
        else:  # nacitani ze souboru
            if len(m.input_in) == 0:
                self.args['arg1']['frame'].change_var(self.args['arg1']['var'], Nil())
            else:
                try:
                    if self.args['arg2']['val'] == 'int':
                        try:
                            self.args['arg1']['frame'].change_var(self.args['arg1']['var'], int(m.input_in[0], 0))
                        except ValueError:
                            self.args['arg1']['frame'].change_var(self.args['arg1']['var'], Nil())
                    elif self.args['arg2']['val'] == 'bool':
                        text = m.input_in[0]
                        if text.lower() == 'true':
                            self.args['arg1']['frame'].change_var(self.args['arg1']['var'], True)
                        else:
                            self.args['arg1']['frame'].change_var(self.args['arg1']['var'], False)
                    elif self.args['arg2']['val'] == 'string':
                        self.args['arg1']['frame'].change_var(self.args['arg1']['var'], m.input_in[0])
                    elif self.args['arg2']['val'] == 'float':
                        value = m.input_in[0]
                        try:
                            self.args['arg1']['frame'].change_var(self.args['arg1']['var'], float(value))
                        except ValueError:
                            try:
                                self.args['arg1']['frame'].change_var(self.args['arg1']['var'], float.fromhex(value))
                            except ValueError:
                                self.args['arg1']['frame'].change_var(self.args['arg1']['var'], Nil())
                    else:
                        sys.exit(32)
                except EOFError:
                    self.args['arg1']['frame'].change_var(self.args['arg1']['var'], Nil())
                except IndexError:
                    self.args['arg1']['frame'].change_var(self.args['arg1']['var'], Nil())
                m.input_in.pop(0)

    def __write(self, m) -> None:
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

    def __concat(self, m) -> None:
        self.__check_dest_var()
        if type(self.args['arg2']['val']) != str or type(self.args['arg3']['val']) != str:
            sys.exit(53)
        else:
            self.args['arg1']['frame'].change_var(self.args['arg1']['var'],
                                                  self.args['arg2']['val'] + self.args['arg3']['val'])

    def __strlen(self, m) -> None:
        self.__check_dest_var()
        if type(self.args['arg2']['val']) != str:
            sys.exit(53)
        else:
            self.args['arg1']['frame'].change_var(self.args['arg1']['var'], len(self.args['arg2']['val']))

    def __getchar(self, m) -> None:
        self.__check_dest_var()
        if type(self.args['arg2']['val']) != str or type(self.args['arg3']['val']) != int:
            sys.exit(53)
        if self.args['arg3']['val'] < 0 or self.args['arg3']['val'] >= len(self.args['arg2']['val']):
            sys.exit(58)
        self.args['arg1']['frame'].change_var(self.args['arg1']['var'],
                                              self.args['arg2']['val'][self.args['arg3']['val']])

    def __setchar(self, m) -> None:
        self.__check_dest_var()
        if self.args['arg1']['val'] is None:
            sys.exit(56)
        if type(self.args['arg1']['val']) != str:
            sys.exit(53)
        if type(self.args['arg2']['val']) != int:
            sys.exit(53)
        if type(self.args['arg3']['val']) != str:
            sys.exit(53)
        if self.args['arg2']['val'] >= len(self.args['arg1']['val']) or self.args['arg2']['val'] < 0\
                or len(self.args['arg3']['val']) == 0:
            sys.exit(58)
        first = self.args['arg1']['val'][:self.args['arg2']['val']]
        second = self.args['arg1']['val'][self.args['arg2']['val'] + 1:]
        self.args['arg1']['frame'].change_var(self.args['arg1']['var'],
                                              first + self.args['arg3']['val'][0] + second)

    def __type(self, m) -> None:
        self.__check_dest_var()
        if type(self.args['arg2']['val']) == int:
            self.args['arg1']['frame'].change_var(self.args['arg1']['var'], 'int')
        elif type(self.args['arg2']['val']) == float:
            self.args['arg1']['frame'].change_var(self.args['arg1']['var'], 'float')
        elif type(self.args['arg2']['val']) == str:
            self.args['arg1']['frame'].change_var(self.args['arg1']['var'], 'string')
        elif type(self.args['arg2']['val']) == bool:
            self.args['arg1']['frame'].change_var(self.args['arg1']['var'], 'bool')
        elif type(self.args['arg2']['val']) == Nil:
            self.args['arg1']['frame'].change_var(self.args['arg1']['var'], 'nil')
        elif self.args['arg2']['type'] == 'var' and self.args['arg2']['val'] is None:
            self.args['arg1']['frame'].change_var(self.args['arg1']['var'], '')
        else:
            sys.exit(53)

    def __label(self, m) -> None:
        pass

    def __jump(self, m) -> None:
        if self.args['arg1']['val'] not in m.xml_parser.labels:
            sys.exit(52)
        m.ins_pointer = m.xml_parser.labels[self.args['arg1']['val']] - 1

    def __jumpifeq(self, m) -> None:
        if self.args['arg1']['val'] not in m.xml_parser.labels:
            sys.exit(52)
        if (isinstance(self.args['arg2']['val'], type(self.args['arg3']['val']))
            and isinstance(self.args['arg3']['val'], type(self.args['arg2']['val']))) or \
                type(self.args['arg2']['val']) is Nil or type(self.args['arg3']['val']) is Nil:
            if self.args['arg2']['val'] == self.args['arg3']['val']:
                m.ins_pointer = m.xml_parser.labels[self.args['arg1']['val']] - 1
            elif type(self.args['arg2']['val']) is Nil and type(self.args['arg3']['val']) is Nil:
                m.ins_pointer = m.xml_parser.labels[self.args['arg1']['val']] - 1
        else:
            sys.exit(53)

    def __jumpifneq(self, m) -> None:
        if self.args['arg1']['val'] not in m.xml_parser.labels:
            sys.exit(52)
        if (isinstance(self.args['arg2']['val'], type(self.args['arg3']['val']))
                and isinstance(self.args['arg3']['val'], type(self.args['arg2']['val']))) or \
                type(self.args['arg2']['val']) is Nil or type(self.args['arg3']['val']) is Nil:
            if type(self.args['arg2']['val']) is Nil and type(self.args['arg3']['val']) is Nil:
                pass
            elif self.args['arg2']['val'] != self.args['arg3']['val']:
                m.ins_pointer = m.xml_parser.labels[self.args['arg1']['val']] - 1
        else:
            sys.exit(53)

    def __exit(self, m) -> None:
        if type(self.args['arg1']['val']) != int:
            sys.exit(53)
        elif self.args['arg1']['val'] < 0 or self.args['arg1']['val'] > 49:
            sys.exit(57)
        else:
            m.ins_pointer = len(m.xml_parser.instructions) + 1
            m.exit_code = self.args['arg1']['val']

    def __dprint(self, m) -> None:
        print(str(self.args['arg1']['val']), file=sys.stderr)

    def __break(self, m) -> None:
        print(f"Pozice vykonavane instrukce: {m.ins_pointer}", file=sys.stderr)
        print(f"Zasobnik volani: {m.call_stack}", file=sys.stderr)
        print(f"Zasobnik ramcu: {m.frame_stack}", file=sys.stderr)
        print(f"Zasobnik dat: {m.data_stack}", file=sys.stderr)
        print(f"Obsah lokalniho ramce: {m.frame_stack[0].frame}", file=sys.stderr)
        print(f"Obsah docasneho ramce: {m.temporary_frame.frame}", file=sys.stderr)
        print(f"Obsah globalniho ramce: {m.global_frame.frame}", file=sys.stderr)
        print(f"Pocet vykonanych instrukci: {m.insts}", file=sys.stderr)

    """Zasobnikove instrukce rozsireni STACK"""
    def __clears(self, m) -> None:
        m.data_stack.clear()

    def __adds(self, m) -> None:
        self.__check_stack_two_operands(m)
        if not ((type(self.args['arg2']['val']) == int and type(self.args['arg3']['val']) == int) or
                (type(self.args['arg2']['val']) == float and type(self.args['arg3']['val']) == float)):
            sys.exit(53)
        elif type(self.args['arg2']['val']) == float:
            m.data_stack.insert(0, {'type': 'float', 'val': self.args['arg2']['val'] + self.args['arg3']['val']})
        else:
            m.data_stack.insert(0, {'type': 'int', 'val': self.args['arg2']['val'] + self.args['arg3']['val']})

    def __subs(self, m) -> None:
        self.__check_stack_two_operands(m)
        if not ((type(self.args['arg2']['val']) == int and type(self.args['arg3']['val']) == int) or
                (type(self.args['arg2']['val']) == float and type(self.args['arg3']['val']) == float)):
            sys.exit(53)
        elif type(self.args['arg2']['val']) == float:
            m.data_stack.insert(0, {'type': 'float', 'val': self.args['arg2']['val'] - self.args['arg3']['val']})
        else:
            m.data_stack.insert(0, {'type': 'int', 'val': self.args['arg2']['val'] - self.args['arg3']['val']})

    def __muls(self, m) -> None:
        self.__check_stack_two_operands(m)
        if not ((type(self.args['arg2']['val']) == int and type(self.args['arg3']['val']) == int) or
                (type(self.args['arg2']['val']) == float and type(self.args['arg3']['val']) == float)):
            sys.exit(53)
        elif type(self.args['arg2']['val']) == float:
            m.data_stack.insert(0, {'type': 'float', 'val': self.args['arg2']['val'] * self.args['arg3']['val']})
        else:
            m.data_stack.insert(0, {'type': 'int', 'val': self.args['arg2']['val'] * self.args['arg3']['val']})

    def __idivs(self, m) -> None:
        self.__check_stack_two_operands(m)
        if type(self.args['arg2']['val']) != int or type(self.args['arg3']['val']) != int:
            sys.exit(53)
        if self.args['arg3']['val'] == 0:
            sys.exit(57)
        m.data_stack.insert(0, {'type': 'int', 'val': self.args['arg2']['val'] // self.args['arg3']['val']})

    def __lts(self, m) -> None:
        self.__check_stack_two_operands(m)
        if not (isinstance(self.args['arg2']['val'], type(self.args['arg3']['val']))
                and isinstance(self.args['arg3']['val'], type(self.args['arg2']['val']))):
            sys.exit(53)
        if type(self.args['arg2']['val']) is Nil or type(self.args['arg3']['val']) is Nil:
            sys.exit(53)
        if self.args['arg2']['val'] < self.args['arg3']['val']:
            m.data_stack.insert(0, {'type': 'bool', 'val': True})
        else:
            m.data_stack.insert(0, {'type': 'bool', 'val': False})

    def __gts(self, m) -> None:
        self.__check_stack_two_operands(m)
        if not (isinstance(self.args['arg2']['val'], type(self.args['arg3']['val']))
                and isinstance(self.args['arg3']['val'], type(self.args['arg2']['val']))):
            sys.exit(53)
        if type(self.args['arg2']['val']) is Nil or type(self.args['arg3']['val']) is Nil:
            sys.exit(53)
        if self.args['arg2']['val'] > self.args['arg3']['val']:
            m.data_stack.insert(0, {'type': 'bool', 'val': True})
        else:
            m.data_stack.insert(0, {'type': 'bool', 'val': False})

    def __eqs(self, m) -> None:
        self.__check_stack_two_operands(m)
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

    def __ands(self, m) -> None:
        self.__check_stack_two_operands(m)
        if type(self.args['arg2']['val']) != bool or type(self.args['arg3']['val']) != bool:
            sys.exit(53)
        if self.args['arg2']['val'] and self.args['arg3']['val']:
            m.data_stack.insert(0, {'type': 'bool', 'val': True})
        else:
            m.data_stack.insert(0, {'type': 'bool', 'val': False})

    def __ors(self, m) -> None:
        self.__check_stack_two_operands(m)
        if type(self.args['arg2']['val']) != bool or type(self.args['arg3']['val']) != bool:
            sys.exit(53)
        if self.args['arg2']['val'] or self.args['arg3']['val']:
            m.data_stack.insert(0, {'type': 'bool', 'val': True})
        else:
            m.data_stack.insert(0, {'type': 'bool', 'val': False})

    def __nots(self, m) -> None:
        if len(m.data_stack) < 1:
            sys.exit(56)
        self.args['arg1'] = m.data_stack.pop()
        if type(self.args['arg1']['val']) != bool:
            sys.exit(53)
        if self.args['arg1']['val']:
            m.data_stack.insert(0, {'type': 'bool', 'val': False})
        else:
            m.data_stack.insert(0, {'type': 'bool', 'val': True})

    def __int2chars(self, m) -> None:
        if len(m.data_stack) < 1:
            sys.exit(56)
        self.args['arg1'] = m.data_stack.pop()
        if type(self.args['arg1']['val']) != int:
            sys.exit(53)
        if self.args['arg1']['val'] < 0 or self.args['arg1']['val'] > 1114111:
            sys.exit(58)
        m.data_stack.insert(0, {'type': 'string', 'val': chr(self.args['arg1']['val'])})

    def __stri2ints(self, m) -> None:
        self.__check_stack_two_operands(m)
        if type(self.args['arg2']['val']) != str or type(self.args['arg3']['val']) != int:
            sys.exit(53)
        if self.args['arg3']['val'] < 0 or self.args['arg3']['val'] >= len(self.args['arg2']['val']):
            sys.exit(58)
        m.data_stack.insert(0, {'type': 'int', 'val': ord(self.args['arg2']['val'][self.args['arg3']['val']])})

    def __jumpifeqs(self, m) -> None:
        self.__check_stack_two_operands(m)
        if self.args['arg1']['val'] not in m.xml_parser.labels:
            sys.exit(52)
        if (isinstance(self.args['arg2']['val'], type(self.args['arg3']['val']))
            and isinstance(self.args['arg3']['val'], type(self.args['arg2']['val']))) or \
                type(self.args['arg2']['val']) is Nil or type(self.args['arg3']['val']) is Nil:
            if self.args['arg2']['val'] == self.args['arg3']['val']:
                m.ins_pointer = m.xml_parser.labels[self.args['arg1']['val']] - 1
            elif type(self.args['arg2']['val']) is Nil and type(self.args['arg3']['val']) is Nil:
                m.ins_pointer = m.xml_parser.labels[self.args['arg1']['val']] - 1
        else:
            sys.exit(53)

    def __jumpifneqs(self, m) -> None:
        self.__check_stack_two_operands(m)
        if self.args['arg1']['val'] not in m.xml_parser.labels:
            sys.exit(52)
        if (isinstance(self.args['arg2']['val'], type(self.args['arg3']['val']))
            and isinstance(self.args['arg3']['val'], type(self.args['arg2']['val']))) or \
                type(self.args['arg2']['val']) is Nil or type(self.args['arg3']['val']) is Nil:
            if type(self.args['arg2']['val']) is Nil and type(self.args['arg3']['val']) is Nil:
                pass
            elif self.args['arg2']['val'] != self.args['arg3']['val']:
                m.ins_pointer = m.xml_parser.labels[self.args['arg1']['val']] - 1
        else:
            sys.exit(53)

    """Instrukce specificke pro rozsireni FLOAT"""
    def __int2float(self, m) -> None:
        self.__check_dest_var()
        if self.args['arg2']['val'] is None:
            sys.exit(56)
        if type(self.args['arg2']['val']) != int:
            sys.exit(53)
        self.args['arg1']['frame'].change_var(self.args['arg1']['var'], float(self.args['arg2']['val']))

    def __float2int(self, m) -> None:
        self.__check_dest_var()
        if self.args['arg2']['val'] is None:
            sys.exit(56)
        if type(self.args['arg2']['val']) != float:
            sys.exit(53)
        self.args['arg1']['frame'].change_var(self.args['arg1']['var'], int(self.args['arg2']['val']))

    def __div(self, m) -> None:
        self.__check_dest_var()
        if type(self.args['arg2']['val']) != float or type(self.args['arg3']['val']) != float:
            sys.exit(53)
        if self.args['arg3']['val'] == 0:
            sys.exit(57)
        self.args['arg1']['frame'].change_var(self.args['arg1']['var'],
                                              self.args['arg2']['val'] / self.args['arg3']['val'])

    def __check_dest_var(self) -> None:
        """Metoda pro kontrolu cilove promenne"""
        if self.args['arg1']['type'] != 'var':
            sys.exit(32)

    def __check_var(self, key) -> None:
        """Kontrola existence promenne"""
        if self.args[key]['frame'] is None:
            sys.exit(55)
        if self.args[key]['var'] not in self.args[key]['frame'].frame and self.opcode != 'DEFVAR':
            sys.exit(54)

    def __check_stack_two_operands(self, m) -> None:
        """Nacteni operandu zasobnikovych instrukci pro instrukce se dvema operandy"""
        if len(m.data_stack) < 2:
            sys.exit(56)
        self.args['arg3'] = m.data_stack.pop(0)
        self.args['arg2'] = m.data_stack.pop(0)
