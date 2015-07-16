import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.nio.file.FileSystems;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.logging.Handler;
import java.util.logging.FileHandler;
import java.util.logging.Level;
import java.util.logging.Logger;
import java.util.logging.SimpleFormatter;

class Disassembler {
    private static final Logger logger = createLogger();
    private static final Instruction[] INSTRUCTION_TABLE = getInstructions();
    private byte[] data;
    private int index;
    private int end;
    private int digits;

    private static class Instruction {
        public final String mnem;
        public final int size;

        public Instruction(String m, int s) {
            mnem = m;
            size = s;
        }
    }

    private static Logger createLogger() {
        Handler fh = null;

        try {
            fh = new FileHandler("logs/Disassembler.java.log");
        } catch (IOException e) {
            e.printStackTrace();
            System.exit(0);
        }

        Logger logger = Logger.getLogger(Disassembler.class.getName());
        logger.setUseParentHandlers(false);
        SimpleFormatter formatter = new SimpleFormatter();
        fh.setFormatter(formatter);
        logger.addHandler(fh);
        
        return logger;
    }

    /*
     * JSON array of arrays from file.
     * Each instruction is represented as an array, like:
     *   ["mvi    c,",  2]
     * where the first element is the mnemonic and the second is the size of 
     * the instruction in bytes.
     *
     * The array indices correspond to the opcodes of the Intel 8080 (i.e. 0x00 
     * through 0xff)
     */
    private static Instruction[] getInstructions() {
        BufferedReader br = null;
        Instruction[] table = new Instruction[256];
        int count = 0;
        String line = null;

        try {
            br = new BufferedReader(new FileReader("instructions.json"));

            while (null != (line = br.readLine())) {
                // Not a good implementation, but doesn't require other 
                // dependencies
                if (line.length() < 23) {
                    continue;
                }

                final int first = line.indexOf("\"") + 1;
                final int last = line.indexOf("\",");
                final String mnem = line.substring(first, last);
                final int size = Character.getNumericValue(line.charAt(20));

                final Instruction instr = new Instruction(mnem, size);
                table[count] = instr;
                count++;
            }
        } catch (IOException e) {
            e.printStackTrace();
            System.exit(0);
        } finally {
            try {
                if (null != br) {
                    br.close();
                }
            } catch (IOException e) {
                e.printStackTrace();
            }
        }

        return table;
    }

    public Disassembler(String filename) {
        Path p = FileSystems.getDefault().getPath("", filename);
        try {
            data = Files.readAllBytes(p);
        } catch (IOException e) {
            e.printStackTrace();
            System.exit(0);
        }
        index = 0;
        end = data.length;
        digits = String.valueOf(end).length();
    }

    private String output1Byte(final Instruction instr) {
        return String.format("%04x %s", index, instr.mnem);
    }

    private String output2Byte(final Instruction instr, final int operand) {
        if (instr.mnem.contains("out") || instr.mnem.contains("in")) {
            return String.format("%04x %s$%02x", index, instr.mnem, operand);
        }

        return String.format("%04x %s#%02x", index, instr.mnem, operand);
    }

    private String output3Byte(final Instruction instr, final int[] operand) {
        if (instr.mnem.contains("lxi")) {
            return String.format("%04x %s#%02x%02x", index, instr.mnem, 
                operand[0], operand[1]);
        }

        return String.format("%04x %s$%02x%02x", index, instr.mnem, operand[0], 
            operand[1]);
    }

    public void run() {
        while (index < end) {
            // Convert signed byte 
            final int b = data[index] & 0xff;
            final Instruction instr = INSTRUCTION_TABLE[b];
            String msg = null;

            if (instr.size == 1) {
                msg = output1Byte(instr);
            } else if (instr.size == 2) {
                int operand = data[index + 1] & 0xff;
                msg = output2Byte(instr, operand);
            } else if (instr.size == 3) {
                int[] operand = new int[2];
                operand[0] = data[index + 2] & 0xff;
                operand[1] = data[index + 1] & 0xff;
                msg = output3Byte(instr, operand);
            }

            index += instr.size;

            System.out.println(msg);
            logger.log(Level.FINE, msg);
        }
    }

    public static void main(String[] args) {
        if (args.length != 1) {
            System.out.println("Usage: java Disassembler [filename]");
            System.exit(0);
        }

        String filename = args[0];

        Disassembler d = new Disassembler(filename);
        d.run();
    }
}

