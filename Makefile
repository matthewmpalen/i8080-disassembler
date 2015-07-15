all: DisassemblerCpp DisassemblerJava DisassemblerGo

DisassemblerCpp:
	g++ -Wall -g -std=c++11 Disassembler.cpp -o DisassemblerCpp

DisassemblerJava:
	javac Disassembler.java

DisassemblerGo:
	go build -o disassembler_go disassembler.go
