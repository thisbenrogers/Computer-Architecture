"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.bytes = [0] * 256
        self.registers = [0] * 8
        self.running = True
        self.PC = 0

    # *     Memory Address Register == (MAR)
    # *     Memory Data Register == (MDR)

    def ram_read(self, MAR):
        # *     Should return the value listed at the given address in memory
        return self.registers[MAR]

    def ram_write(self, MAR, MDR):
        # *     Should write the value to the given address in memory
        self.registers[MAR] = MDR
        return None

    def load(self):
        """Load a program into memory."""

        address = 0

        # For now, we've just hardcoded a program:

        program = [
            # From print8.ls8
            0b10000010, # LDI R0,8
            0b00000000,
            0b00001000,
            0b01000111, # PRN R0
            0b00000000,
            0b00000001, # HLT
        ]

        for instruction in program:
            self.ram[address] = instruction
            address += 1


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
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
            IR = register[pc]
            operand_a, operand_b = register[pc+1], register[pc+2]
            if IR == "HLT":
                self.running = False
            if IR == "LDI":
                self.ram_write(operand_a, operand_b)
                self.PC += 2
            if IR == "PRN":
                pass
