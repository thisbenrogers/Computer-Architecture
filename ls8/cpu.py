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
        self.FL = 0b00000000
        # *     program counter
        self.pc = 0
        # *     program commands
        self.HLT = 0b00000001
        self.LDI = 0b10000010
        self.PRN = 0b01000111
        self.ADD = 0b10100000
        self.MUL = 0b10100010
        self.DIV = 0b10100011
        self.POP = 0b01000110
        self.PUSH = 0b01000101
        self.CALL = 0b01010000
        self.RET = 0b00010001
        self.CMP = 0b10100111
        self.JMP = 0b01010100
        self.JEQ = 0b01010101
        self.JNE = 0b01010110

        self.breaktable = {}
        self.breaktable[self.HLT] = self.handle_HLT
        self.breaktable[self.LDI] = self.handle_LDI
        self.breaktable[self.PRN] = self.handle_PRN
        self.breaktable[self.ADD] = self.handle_ADD
        self.breaktable[self.MUL] = self.handle_MUL
        self.breaktable[self.DIV] = self.handle_DIV
        self.breaktable[self.POP] = self.handle_POP
        self.breaktable[self.PUSH] = self.handle_PUSH
        self.breaktable[self.CALL] = self.handle_CALL
        self.breaktable[self.RET] = self.handle_RET
        self.breaktable[self.CMP] = self.handle_CMP
        self.breaktable[self.JMP] = self.handle_JMP
        self.breaktable[self.JEQ] = self.handle_JEQ
        self.breaktable[self.JNE] = self.handle_JNE

    def handle_HLT(self):
        self.running = False
        return None

    def handle_LDI(self, op_a, op_b):
        self.reg[op_a] = op_b
        return None

    def handle_PRN(self, op_a):
        print(self.reg[op_a])
        return None

    def handle_MUL(self, op_a, op_b):
        self.alu("MUL", op_a, op_b)
        return None

    def handle_ADD(self, op_a, op_b):
        self.alu("ADD", op_a, op_b)
        return None
    
    def handle_DIV(self, op_a, op_b):
        self.alu("DIV", op_a, op_b)
        return None

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
        return None

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
        return None

    def handle_CALL(self, reg_num):
        # *     Push the return address onto the Stack
        ret_addr = self.pc + 2
        self.reg[7] -= 1
        stack_pointer = self.reg[7]
        self.ram_write(stack_pointer, ret_addr)
        # *     Jump, set the PC to wherever the register says
        address_jump = self.reg[reg_num]
        self.pc = address_jump
        return None

    def handle_RET(self):
        stack_pointer = self.reg[7]
        return_address = self.ram[stack_pointer]
        self.reg[7] += 1
        self.pc = return_address
        return None

    def handle_CMP(self, reg_a, reg_b):
        self.alu("CMP", reg_a, reg_b)
        return None

    def handle_JMP(self, reg_addr):
        self.pc = self.reg[reg_addr]
        return None

    def handle_JEQ(self, reg_addr):
        if self.FL == 0b00000001:
            self.pc = self.reg[reg_addr]
        else:
            self.pc += 2
        return None

    def handle_JNE(self, reg_addr):
        if self.FL == 0b00000010 or self.FL == 0b00000100:
            self.pc = self.reg[reg_addr]
        else:
            self.pc += 2
        return None


    # *     Memory Address Register == (MAR)
    # *     Memory Data Register == (MDR)
    def ram_read(self, MAR):
        # *     Should return the value listed at the given address in memory
        return self.ram[MAR]

    def ram_write(self, MAR, MDR):
        # *     Should write the value to the given address in memory
        self.ram[MAR] = MDR
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
                        # print(f'command: {command}')
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
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "DIV":
            self.reg[reg_a] /= self.reg[reg_b]
        elif op == "CMP":
            if self.reg[reg_a] == self.reg[reg_b]:
                self.FL = 0b00000001
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.FL = 0b00000010
            elif self.reg[reg_a] < self.reg[reg_b]:
                self.FL = 0b00000100
            else:
                self.FL = 0b00000000
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

            # print(f'IR in run: {IR}')

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

            # *     Determines increment of self.pc based on a bitshifting of the command,
            # *     Unless the IR command handles self.pc internally
            # *         (The binary representation of each command 
            # *         has the number of args built into its first 2 registers)
            if IR != 0b01010000 and IR != 0b00010001 and IR != 0b01010100 and IR != 0b01010101 and IR != 0b01010110:
                number_of_operands = IR >> 6
                self.pc += (1 + number_of_operands)
        return None

