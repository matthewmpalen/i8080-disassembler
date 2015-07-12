# Python
require "json"
require "optparse"
require "logger"

LOGGER = Logger.new("logs/disassembler.rb.log")
LOGGER.level = Logger::WARN

def get_instructions
<<-DOC
  JSON array of arrays from file.
  Each instruction is represented as an array, like:
    ["mvi    c,",  2]

  where the first element is the mnemonic and the second is the size of the 
  the instruction in bytes.

  There must be a total of 256 instructions to be complete. The array indices 
  correspond to the opcodes of Intel 8080 (i.e. 0x00 through 0xff)
DOC
  begin
      f = File.read("instructions.json")
      file_data = JSON.parse(f)
  rescue Errno::ENOENT => e
      LOGGER.error(e)
      exit
  end

  unless file_data.length == 256
      LOGGER.error('Incomplete instruction set')
      exit
  end

  return file_data
end

INSTRUCTION_TABLE = get_instructions()

class Disassembler
  def initialize(filename)
    begin
      @data = File.binread(filename)
    rescue Errno::ENOENT => e
      LOGGER.error(e)
      exit
    end
    
    @index = 0
    @end = @data.length
    @digits = @end.to_s.length
  end

  def output(size, mnem, operand=None)
<<-DOC
    Output immediate operands prepended with the '#' character.
    Output address operands prepended with the '$' character.
DOC
    token = mnem.split()[0]

    case size
    when 1
      return "%04x %s" % [@index, mnem]
    when 2
      if ['out', 'in'].include? token
        return "%04x %s$%02x" % [@index, mnem, operand]
      else
        return "%04x %s#%02x" % [@index, mnem, operand]
      end
    when 3
      if ['lxi'].include? token
        return "%04x %s#%04x" % [@index, mnem, operand]
      else
        return "%04x %s$%04x" % [@index, mnem, operand]
      end
    end
  end

  def run()
    while @index < @end
      byte = @data[@index].ord
      mnem = INSTRUCTION_TABLE[byte][0]
      size = INSTRUCTION_TABLE[byte][1]

      case size
      when 1
        operand = nil
      when 2
        operand = @data[@index + 1].ord
      when 3
        start = @index + 1
        end_ = start + 2
        operand = @data[start..end_].unpack('<S_')[0]
      end

      msg = output(size, mnem, operand=operand)
      @index += size

      puts msg
      LOGGER.debug(msg)
    end
  end
end

def main
  options = {}
  OptionParser.new do |opts|
    opts.banner = "Usage: disassembler.rb [filename]"

    opts.on("-h", "--help", "Prints this help") do
      puts opts
      exit
    end
  end.parse!

  filename = ARGV[0]
  d = Disassembler.new(filename)
  d.run()
end

if __FILE__ == $0
  main()
end
