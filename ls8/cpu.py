"""CPU functionality."""

import sys
from inspect import signature

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        # *     registers, R0-R7
        self.reg = [0] * 8
        # *     set Stack pointer
        self.reg[7] = 0xF4
        self.ram = [0] * 256
        self.running = True
        # *     program counter
        self.pc = 0
        self.LDI = 0b10000010
        self.PRN = 0b01000111
        self.HLT = 0b00000001
        self.MUL = 0b10100010
        self.DIV = 0b10100011
        self.POP = 0b01000110
        self.PUSH = 0b01000101
        self.CALL = 0b01010000
        self.RET = 0b00010001

        self.breaktable = {}
        self.breaktable[self.HLT] = self.handle_HLT
        self.breaktable[self.LDI] = self.handle_LDI
        self.breaktable[self.PRN] = self.handle_PRN
        self.breaktable[self.MUL] = self.handle_MUL
        self.breaktable[self.DIV] = self.handle_DIV
        self.breaktable[self.POP] = self.handle_POP
        self.breaktable[self.PUSH] = self.handle_PUSH

    def handle_HLT(self):
        self.running = False
        return None

    def handle_LDI(self, op_a, op_b):
        self.ram_write(op_a, op_b)
        return None

    def handle_PRN(self, op_a):
        print(self.ram_read(op_a))

    def handle_MUL(self, op_a, op_b):
        self.alu("MUL", op_a, op_b)
    
    def handle_DIV(self, op_a, op_b):
        self.alu("DIV", op_a, op_b)

    def handle_POP(self):
        # *     stack pointer
        sp = self.reg[7]

        # *     value from memory at pointed address
        value = self.ram[sp]

        # *     target reg address
        reg_address = self.ram[self.pc + 1]

        # *     write the value to the register
        self.reg[reg_address] = value

        # *     increment the stack pointer
        self.reg[7] += 1

    def handle_PUSH(self):
        # *     decrement stack pointer
        self.reg[7] -= 1

        # *     get register address
        reg_address = self.ram[self.pc + 1]

        # *     get value from register address
        value = self.reg[reg_address]

        # *     copy to top of stack
        sp = self.reg[7]
        self.ram[sp] = value

    # *     Memory Address Register == (MAR)
    # *     Memory Data Register == (MDR)
    def ram_read(self, MAR):
        # *     Should return the value listed at the given address in memory
        return self.reg[MAR]

    def ram_write(self, MAR, MDR):
        # *     Should write the value to the given address in memory
        self.reg[MAR] = MDR
        return None

    def load(self):
        """Load a program into memory."""

        try:
            if len(sys.argv) < 2:
                print(f'Error from {sys.argv[0]}: missing filename argument')
                print(f'Usage: python3 {sys.argv[0]} <somefilename>')
                sys.exit(1)

            # add a counter that adds to memory at that index
            ram_index = 0

            with open(sys.argv[1]) as f:
                for line in f:
                    split_line = line.split("#")[0]
                    stripped_split_line = split_line.strip()

                    if stripped_split_line != "":
                        command = int(stripped_split_line, 2)
                        
                        # load command into memory
                        self.ram[ram_index] = command
                        ram_index += 1

        except FileNotFoundError:
            print(f'Error from {sys.argv[0]}: {sys.argv[1]} not found')
            print("(Did you double check the file name?)")

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        if op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        if op == "DIV":
            self.reg[reg_a] /= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        while self.running:
            # *     creates variable for the current and next binary values from self.ram
            IR = self.ram[self.pc]
            operand_a = self.ram[self.pc + 1]
            operand_b = self.ram[self.pc + 2]

            # *     Finding out how many arguments to pass the breaktable functions
            sig = signature(self.breaktable[IR])
            params = sig.parameters
            num_params = len(params)

            # *     Calls the function with the appropriate num of args
            if num_params == 0:
                self.breaktable[IR]()
            if num_params == 1:
                self.breaktable[IR](operand_a)
            if num_params >= 2:
                self.breaktable[IR](operand_a, operand_b)

            # *     Determines increment of self.pc based on a bitshifting of the command
            # *         (The binary representation of each command 
            # *         has the number of args built into its first 2 registers)
            number_of_operands = IR >> 6
            self.pc += (1 + number_of_operands)

