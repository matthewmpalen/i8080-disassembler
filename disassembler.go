package main

import (
    "encoding/json"
    "flag"
    "fmt"
    "io/ioutil"
    "reflect"
)

type jsonInstructionTable [][]interface{}

type Instruction struct {
    mnem string
    size int
}

type Disassembler struct {
    data []byte
    index int
    end int
    digits int
}

func check(e error) {
    if e != nil {
        panic(e)
    }
}

/* JSON array of arrays from file.
 * Each instruction is represented as an array, like:
 *   ["mvi    c,",  2]
 * where the first element is the mnemonic and the second is the size of the 
 * instruction in bytes.
 *
 * The array indices correspond to the opcodes of the Intel 8080 (i.e. 0x00 
 * through 0xff)
 */
func getInstructions() [256]Instruction {
    f, err := ioutil.ReadFile("instructions.json")
    check(err)

    var jsonData jsonInstructionTable
    err = json.Unmarshal(f, &jsonData)
    check(err)

    var instructionTable [256]Instruction

    for i, elem := range jsonData {
        var instr Instruction

        for _, data := range elem {
            switch d := data.(type) {
            default:
                fmt.Printf("Unrecognized type: %v", reflect.TypeOf(d))
            case float64:
                instr.size = int(d)
            case string:
                instr.mnem = d
            }

        }
        
        instructionTable[i] = instr
    }

    return instructionTable
}

func NewDisassembler(filename string) *Disassembler {
    d := new(Disassembler)
    data, err := ioutil.ReadFile(filename)
    check(err)
    d.data = data
    d.index = 0
    d.end = len(d.data)
    d.digits = 4
    return d
}

func (d Disassembler) output1Byte(instr Instruction) string {
    return fmt.Sprintf("%04x %s", d.index, instr.mnem)
}

func (d Disassembler) output2Byte(instr Instruction, operand byte) string {
    special := []string{"out", "in"}
    for _, s := range special {
        if instr.mnem == s {
            return fmt.Sprintf("%04x %s$%02x", d.index, instr.mnem, operand)
        }
    }

    return fmt.Sprintf("%04x %s#%02x", d.index, instr.mnem, operand)
}

func (d Disassembler) output3Byte(instr Instruction, operand []byte) string {
    if instr.mnem == "lxi" {
        return fmt.Sprintf("%04x %s#%04x", d.index, instr.mnem, operand)
    }

    return fmt.Sprintf("%04x %s$%04x", d.index, instr.mnem, operand)
}

func (d Disassembler) Run() {
    for d.index < d.end {
        byte := d.data[d.index]
        instr := INSTRUCTION_TABLE[byte]

        var msg string

        if instr.size == 1 {
            msg = d.output1Byte(instr)
        } else if instr.size == 2 {
            operand := d.data[d.index + 1]
            msg = d.output2Byte(instr, operand)
        } else if instr.size == 3 {
            operand := make([]uint8, 2)
            operand[0] = d.data[d.index + 2]
            operand[1] = d.data[d.index + 1]
            msg = d.output3Byte(instr, operand)
        }

        fmt.Println(msg)
        d.index += instr.size
    }
}

var INSTRUCTION_TABLE = getInstructions()

func main() {
    var filename string
    flag.StringVar(&filename, "filename", "roms/invaders.rom", 
        "File to be disassembled")
    flag.Parse()

    d := NewDisassembler(filename)
    d.Run()
}
