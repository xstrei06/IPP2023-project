import sys
from instruction import Instruction
from frame import Frame
from xmlparser import XMLParser
from argumentparser import ArgumentParser
from statistics import Statistics


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

        self.stats = Statistics(self.parser.stats_file, self.parser.stats)
        self.insts = 0
        self.hot = 0
        self.hot_order = 0
        self.vars = 0

        self.exit_code = 0

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

    def count_available_vars(self):
        count = len(self.global_frame.frame)
        if self.frame_stack[0] is not None:
            count += len(self.frame_stack[0].frame)
        if self.temporary_frame is not None:
            count += len(self.temporary_frame.frame)
        if self.vars < count:
            self.vars = count


if __name__ == "__main__":

    main = Main()

    while True:
        main.ins_pointer += 1
        if main.ins_pointer >= len(main.instructions):
            break
        main.instructions[main.ins_pointer].execute(main)

    if main.stats.stats_file is not None:
        main.stats.print_stats(main)

    sys.exit(main.exit_code)
