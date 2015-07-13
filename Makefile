all: DisassemblerGo

DisassemblerGo:
	go build -o disassembler_go disassembler.go
