#include <fstream>
#include <iostream>
#include <iterator>
#include <string>
#include <vector>

using namespace std;

struct Instruction {
    string mnem;
    unsigned int size;

    Instruction(const string& m, unsigned int s);
};

Instruction::Instruction(const string& m, unsigned int s): mnem(m), size(s) {};

class Disassembler {
private:
    vector<char> data;
    unsigned int index;
    size_t end;
    unsigned int digits;

    string output1Byte(const Instruction& instr) const;
    string output2Byte(const Instruction& instr, unsigned char operand) const;
    string output3Byte(const Instruction& instr, unsigned char operand[2]) const;
public:
    Disassembler(char* filename);
    void run();
};

/*
 * JSON array of arrays from file.
 * Each instruction is represented as an array, like:
 *   ["mvi    c,",  2]
 * where the first element is the mnemonic and the second is the size of the 
 * instruction in bytes.
 *
 * The array indices correspond to the opcodes of the Intel 8080 (i.e. 0x00 
 * through 0xff)
 */
vector<Instruction> getInstructions() {
    ifstream f("instructions.json");
    if (!f.is_open()) {
        cout << "Instructions file not found!" << endl;
        exit(0);
    }
   
    vector<Instruction> table;
    string line;
    while (getline(f, line)) {
        // Not a good implementation, but doesn't require other dependencies
        if (line.size() < 23) {
            continue;
        }

        const size_t first = line.find("\"") + 1;
        const size_t last = line.find("\",");
        const string mnem = line.substr(first, last - first);
        const unsigned int size = stoi(line.substr(20, 1));

        const Instruction instr(mnem, size);
        table.push_back(instr);
    }

    f.close();

    return table;
}

Disassembler::Disassembler(char* filename): index(0), digits(4) {
    ifstream f(filename, ios::binary);
    if (!f.is_open()) {
        cout << filename << " is not a file!" << endl;
        exit(0);
    }

    data = vector<char>(istreambuf_iterator<char>(f), 
        istreambuf_iterator<char>());

    f.close();

    end = data.size();
}

string Disassembler::output1Byte(const Instruction& instr) const {
    const int size = 22;
    char buffer[size];
    snprintf(buffer, size, "%04x %s", index, instr.mnem.c_str());
    return string(buffer);
}

string Disassembler::output2Byte(const Instruction& instr, 
        unsigned char operand) const {
    const int size = 22;
    char buffer[size];

    if (instr.mnem.find("out") != string::npos || 
        instr.mnem.find("in") != string::npos) {
        snprintf(buffer, size, "%04x %s$%02x", index, instr.mnem.c_str(), 
            operand);
    } else {
        snprintf(buffer, size, "%04x %s#%02x", index, instr.mnem.c_str(), 
            operand);
    }

    return string(buffer);
}

string Disassembler::output3Byte(const Instruction& instr, 
        unsigned char operand[2]) const {
    const int size = 22;
    char buffer[size];

    if (instr.mnem.find("lxi") != string::npos) {
        snprintf(buffer, size, "%04x %s#%02x%02x", index, instr.mnem.c_str(), 
            operand[0], operand[1]);
    } else {
        snprintf(buffer, size, "%04x %s$%02x%02x", index, instr.mnem.c_str(), 
            operand[0], operand[1]);
    }

    return string(buffer);
}

const vector<Instruction> instructionTable = getInstructions();

void Disassembler::run() {
    while (index < end) {
        const unsigned char byte = data[index];
        const Instruction instr = instructionTable[byte];
        string msg;

        if (instr.size == 1) {
            msg = output1Byte(instr);
        } else if (instr.size == 2) {
            unsigned char operand = data[index + 1];
            msg = output2Byte(instr, operand);
        } else if (instr.size == 3) {
            unsigned char operand[2];
            operand[0] = data[index + 2];
            operand[1] = data[index + 1];
            msg = output3Byte(instr, operand);
        }

        index += instr.size;

        cout << msg << endl;
    }
}

int main(int argc, char* argv[]) {
    if (argc != 2) {
        cout << "Usage: ./Disassembler [filename]" << endl;
        exit(0);
    }

    char* filename = argv[1];

    Disassembler d(filename);
    d.run();

    return 0;
}
