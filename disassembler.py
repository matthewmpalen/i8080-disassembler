# Python
from argparse import ArgumentParser
import json
import logging
import struct

# External

# Local
from opcodes import Opcode

def get_instructions():
    try:
        with open('instructions.json') as f:
            file_data = json.load(f)
    except FileNotFoundError as e:
        logging.error(e)
        exit()

    if len(file_data) != 256:
        logging.error('Incomplete instruction set')
        exit()

    return file_data

INSTRUCTION_TABLE = get_instructions()

class Disassembler(object):
    def __init__(self, filename):
        try:
            with open(filename, 'rb') as f:
                self._data = f.read()
        except FileNotFoundError as e:
            logging.error(e)
            exit()

        self._index = 0
        self._end = len(self._data)
        self._digits = len(str(len(self._data)))

        logging.basicConfig(level=logging.WARNING, 
            filename='logs/disassembler.py.log', filemode='w')
        logging.getLogger('disassembler')

    def _log(self, index, size, mnem, operand=None):
        token = mnem.split()[0]

        if size == 1:
            return '{0:0{1}x} {2}'.format(index, self._digits, mnem)
        elif size == 2:
            if token in ('out', 'in'):
                return '{0:0{1}x} {2}${3:02x}'.format(index, self._digits, 
                    mnem, operand)
            else:
                return '{0:0{1}x} {2}#{3:02x}'.format(index, self._digits, 
                    mnem, operand)
        elif size == 3:
            if token in ('lxi'):
                return '{0:0{1}x} {2}#{3:04x}'.format(index, self._digits, 
                    mnem, operand)
            else:
                return '{0:0{1}x} {2}${3:04x}'.format(index, self._digits, 
                    mnem, operand)

    def run(self):
        while self._index < self._end:
            byte = self._data[self._index]
            mnem = INSTRUCTION_TABLE[byte][0]
            size = INSTRUCTION_TABLE[byte][1]

            if size == 1:
                operand = None
            elif size == 2:
                operand = self._data[self._index + 1]
            elif size == 3:
                start = self._index + 1
                end = start + 2
                operand = struct.unpack('<H', self._data[start:end])[0]

            msg = self._log(self._index, size, mnem, operand=operand)

            self._index += size
            print(msg)
            logging.debug(msg)

if __name__ == '__main__':
    arg_parser = ArgumentParser()
    arg_parser.add_argument('filename', help='File to be disassembled')
    args = arg_parser.parse_args()
    
    d = Disassembler(args.filename)
    d.run()
