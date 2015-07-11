# Python
from argparse import ArgumentParser
import json
import logging
import struct

def get_instructions():
    """
    JSON array of arrays from file.
    Each instruction is represented as an array, like:
      ["mvi    c,",  2]

    where the first element is the mnemonic and the second is the size of the 
    the instruction in bytes.

    There must be a total of 256 instructions to be complete. The array indices 
    correspond to the opcodes of Intel 8080 (i.e. 0x00 through 0xff)
    """
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

    def _log(self, size, mnem, operand=None):
        """
        Output immediate operands prepended with the '#' character.
        Output addresse operands prepended with the '$' character.
        """
        token = mnem.split()[0]

        if size == 1:
            return '{0:0{1}x} {2}'.format(self._index, self._digits, mnem)
        elif size == 2:
            if token in ('out', 'in'):
                return '{0:0{1}x} {2}${3:02x}'.format(self._index, 
                    self._digits, mnem, operand)
            else:
                return '{0:0{1}x} {2}#{3:02x}'.format(self._index, 
                    self._digits, mnem, operand)
        elif size == 3:
            if token in ('lxi'):
                return '{0:0{1}x} {2}#{3:04x}'.format(self._index, 
                    self._digits, mnem, operand)
            else:
                return '{0:0{1}x} {2}${3:04x}'.format(self._index, 
                    self._digits, mnem, operand)

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

            msg = self._log(size, mnem, operand=operand)
            self._index += size

            print(msg)
            logging.debug(msg)

def main():
    arg_parser = ArgumentParser()
    arg_parser.add_argument('filename', help='File to be disassembled')
    args = arg_parser.parse_args()
    
    d = Disassembler(args.filename)
    d.run()

if __name__ == '__main__':
    main()
