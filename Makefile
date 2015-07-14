all: DisassemblerCpp DisassemblerGo

DisassemblerCpp:
	g++ -Wall -g -std=c++11 Disassembler.cpp -o DisassemblerCpp

DisassemblerGo:
	go build -o disassembler_go disassembler.go
