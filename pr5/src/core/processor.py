from abc import ABC, abstractmethod
from .fu import *
from .riscv_tables import *


class Processor(ABC):
    def __init__(self, start, ram, logger):
        self.pc = start
        self.curr_pc = 0
        self.registers = [0] * 32  # x0 to x31
        self.mem = ram
        self.logr = logger
        self.decoded = {}
        self.ldata = 0

    def fetch(self) -> int:
        """
        Fetch the instruction from memory, and update PC
        returns instruction
        """
        try:
            self.curr_pc = self.pc 
            instruction = self.mem.read_word(self.curr_pc)
            self.logr.debug(f"got instruction {instruction:08x} at {self.curr_pc:08x}")
            return instruction
        except ValueError as e:
            self.logr.error(f"Error fetching instruction at {self.curr_pc:08x}: {e}")
            exit()

    def decode(self, instruction: int):
        """
        Gets an instruction (32-bit integer) and sets the "decoded" dictionary.
        fields in decoded are {"opcode", "rs1", "rs2", "rd", "imm"}
        Ensure that "imm" has a signed value where appropriate
        """
        # Extract the opcode (7 bits)
        opcode = instruction & 0x7F
        self.decoded["opcode"] = opcode

        if opcode == 0x33:  # R-type (Arithmetic)
            funct7 = (instruction >> 25) & 0x7F
            rs2 = (instruction >> 20) & 0x1F
            rs1 = (instruction >> 15) & 0x1F
            funct3 = (instruction >> 12) & 0x07
            rd = (instruction >> 7) & 0x1F
            self.decoded["rs1"] = rs1
            self.decoded["rs2"] = rs2
            self.decoded["rd"] = rd
            self.decoded["funct3"] = funct3
            self.decoded["funct7"] = funct7
            self.decoded["imm"] = 0
        elif opcode == 0x03:  # I-type (Load)
            imm = instruction >> 20
            if (imm > 0x800):
                imm = imm | 0xFFFFF000
                imm = imm - (1 << 32)
            rs1 = (instruction >> 15) & 0x1F
            funct3 = (instruction >> 12) & 0x07
            rd = (instruction >> 7) & 0x1F
            self.decoded["rs1"] = rs1
            self.decoded["rs2"] = 0
            self.decoded["rd"] = rd
            self.decoded["funct3"] = funct3
            self.decoded["funct7"] = 0x00
            self.decoded["imm"] = imm
        elif opcode == 0x13:  # I-type (Immediate Arithmetic)
            imm = instruction >> 20
            if (imm > 0x800):
                imm = imm | 0xFFFFF000
                imm = imm - (1 << 32)
            rs1 = (instruction >> 15) & 0x1F
            funct3 = (instruction >> 12) & 0x07
            rd = (instruction >> 7) & 0x1F
            self.decoded["rs1"] = rs1
            self.decoded["rs2"] = 0
            self.decoded["rd"] = rd
            self.decoded["funct3"] = funct3
            self.decoded["funct7"] = 0x00
            self.decoded["imm"] = imm
        elif opcode == 0x23:  # S-type (Store)
            imm = ((instruction >> 25) << 5) | ((instruction >> 7) & 0x1F)
            if (imm > 0x800):
                imm = imm | 0xFFFFF000
                imm = imm - (1 << 32)
            rs2 = (instruction >> 20) & 0x1F
            rs1 = (instruction >> 15) & 0x1F
            funct3 = (instruction >> 12) & 0x07
            self.decoded["rs1"] = rs1
            self.decoded["rs2"] = rs2
            self.decoded["rd"] = 0
            self.decoded["funct3"] = funct3
            self.decoded["funct7"] = 0x00
            self.decoded["imm"] = imm 
        elif opcode == 0x63:  # B-type (Branch)
            imm_12 = (instruction >> 31) & 0x1
            imm_10_5 = (instruction >> 25) & 0x1F
            imm_4_1 = (instruction >> 8) & 0xF
            imm_11 = (instruction >> 7) & 0x1
            imm = ((imm_12 << 11) | (imm_11 << 10) | (imm_10_5 << 4) | imm_4_1) << 1
            if (imm > 0x1000):
                imm = imm | 0xFFFFF000
                imm = imm - (1 << 32)
            rs2 = (instruction >> 20) & 0x1F
            rs1 = (instruction >> 15) & 0x1F
            funct3 = (instruction >> 12) & 0x07
            self.decoded["rs1"] = rs1
            self.decoded["rs2"] = rs2
            self.decoded["rd"] = 0
            self.decoded["funct3"] = funct3
            self.decoded["funct7"] = 0x00
            self.decoded["imm"] = imm
        elif opcode == 0x37:  # U-type (LUI)
            imm = instruction & 0xFFFFF000
            rd = (instruction >> 7) & 0x1F
            self.decoded["rs1"] = 0
            self.decoded["rs2"] = 0
            self.decoded["rd"] = rd
            self.decoded["funct3"] = 0x0
            self.decoded["funct7"] = 0x00
            self.decoded["imm"] = imm
        elif opcode == 0x17:  # U-type (AUIPC)
            imm = instruction & 0xFFFFF000
            rd = (instruction >> 7) & 0x1F
            self.decoded["rs1"] = 0
            self.decoded["rs2"] = 0
            self.decoded["rd"] = rd
            self.decoded["funct3"] = 0x0
            self.decoded["funct7"] = 0x00
            self.decoded["imm"] = imm
        elif opcode == 0x6F:  # J-type (JAL)
            imm_20 = (instruction >> 31) & 0x1  
            imm_10_1 = (instruction >> 21) & 0x3FF
            imm_11 = (instruction >> 20) & 0x1
            imm_19_12 = (instruction >> 12) & 0xFF
            imm = ((imm_20 << 19) | (imm_19_12 << 11) | (imm_11 << 10) | imm_10_1) << 1
            if (imm > 0x100000):
                imm = imm | 0xFFF00000
                imm = imm - (1 << 32)
            rd = (instruction >> 7) & 0x1F
            self.decoded["rs1"] = 0
            self.decoded["rs2"] = 0
            self.decoded["rd"] = rd
            self.decoded["funct3"] = 0x0
            self.decoded["funct7"] = 0x00
            self.decoded["imm"] = imm
        else:
            self.decoded["opcode"] = opcode
            self.decoded["rs1"] = 0
            self.decoded["rs2"] = 0
            self.decoded["rd"] = 0
            self.decoded["imm"] = 0
            self.decoded["funct3"] = 0x0
            self.decoded["funct7"] = 0x00

        self.logr.debug(f"opcode = {self.decoded["opcode"]:02x}, " + 
                        f"funct3 = {self.decoded["funct3"]:01x}, " + 
                        f"funct7 = {self.decoded["funct7"]:02x}")
        self.op = ((self.decoded["opcode"] << 12) | 
                   (self.decoded["funct3"] << 8) | 
                   (self.decoded["funct7"]))

    def operand_fetch(self):
        rs1 = self.decoded["rs1"]
        rs2 = self.decoded["rs2"]
        v_rs1 = self.registers[rs1] if rs1 != 0 and rs1 != None else 0 
        v_rs2 = self.registers[rs2] if rs2 != 0 and rs2 != None else 0 

        v_imm = self.decoded["imm"]
        self.logr.debug(f"rs1 = {rs1}, rs2 = {rs2}, imm = {hex(v_imm)}")
        v_pc  = self.curr_pc

        self.op1, self.op2 = alu_operands.get(self.op, (None, None))(v_rs1, v_rs2, v_imm, v_pc)
        # FIXME: the choice of the below constant may be correct always
        if (self.op1 > 0xF0000000):
            self.op1 = self.op1 - (1 << 32)

        # FIXME: the choice of the below constant may be correct always
        if (self.op2 > 0xF00000000):
            self.op2 = self.op2 - (1 << 32)
        self.logr.debug(f"op1: {self.op1}, op2: {self.op2}")


    def execute(self):
        """
        Execute the instruction
        decoded_instr, operand1 and operand2 are returned by previous stages
        returns the result of the operation
        """
        # TODO: alu_function is incomplete. Complete it (without modifying fu.py)
        self.result = alu_function.get(self.op, None)(self.op1, self.op2)
        self.logr.debug(f"Result of {self.op:05x} is: {self.result}")

    def update_pc(self):
        """
        Update PC to take a branch or jump
        """
        # TODO: Complete this function appropriately
       
        # Straight-line code is default case
        self.pc = self.curr_pc + 4

    def mem_access(self):
        """
        Access memory based on the instruction.
        """
        inst = self.op
        addr = self.result  # address is generated by execute()

        # Handle load instructions
        if is_load(inst):
            masked_inst = (inst & 0x00F00) >> 8
            if (masked_inst == 0x0 or masked_inst == 0x4):
                self.ldata = self.mem.read(addr)
            elif (masked_inst == 0x1 or masked_inst == 0x5):
                self.ldata = self.mem.read_halfword(addr)
            elif (masked_inst == 0x2):
                self.ldata = self.mem.read_word(addr)
            else:
                self.logr.error(f"Invalid load op {inst:05x}")
                exit()
        
        # Handle store instructions
        rs2 = self.decoded["rs2"]
        data = self.registers[rs2] if rs2 != 0 and rs2 != None else 0 
        if is_store(inst):
            masked_inst = (inst & 0x00F00) >> 8
            if (masked_inst == 0x0):
                self.mem.write(addr, (data & 0xFF))
            elif (masked_inst == 0x1):
                self.mem.write_halfword(addr, (data & 0xFFFF))
            elif (masked_inst == 0x2):
                self.mem.write_word(addr, data)
            else:
                self.logr.error(f"Invalid store op {inst:05x}")
                exit()


    def reg_write(self):
        """
        Write the result of the operation back to the register.
        """
        # NOTE: CAUTION - Changing the outputs here will violate test cases
        inst = self.op
        rd = self.decoded["rd"]
        
        if is_branch(inst):
            self.logr.out(f"{self.curr_pc:08x} | " + 
                          f"next_pc = {self.pc:08x} | " + 
                          f"x? = {0:08x} | " + 
                          f"mem[?] = {0:08x}")
            return
        
        if is_jump(inst):
            self.registers[rd] = self.result
            self.logr.out(f"{self.curr_pc:08x} | " +
                          f"next_pc = {self.pc:08x} | " + 
                          f"x{rd} = {self.registers[rd]:08x} | " +
                          f"mem[?] = {0:08x}")
            return

        if is_unimplemented(inst):
            self.logr.out(f"{self.curr_pc:08x} | " + 
                          f"next_pc = {self.pc:08x} | " + 
                          f"x? = {0:08x} | " + 
                          f"mem[?] = {0:08x} *unimplemented*")
            return

        if is_load(inst):
            self.registers[rd] = self.ldata
            self.logr.out(f"{self.curr_pc:08x} | " + 
                          f"next_pc = {self.pc:08x} | " +
                          f"x{rd} = {self.registers[rd]:08x} | " +
                          f"mem[{self.result:08x}] => {self.ldata:08x}")
            return

        if is_store(inst):
            rs2 = self.decoded["rs2"]
            data = self.registers[rs2] if rs2 != 0 and rs2 != None else 0 
            self.logr.out(f"{self.curr_pc:08x} | " +
                          f"next_pc = {self.pc:08x} | " +
                          f"x? = {0:08x} | " + 
                          f"mem[{self.result:08x}] <= {data:08x}")
            return
        
        # All other instructions
        self.registers[rd] = self.result
        self.logr.out(f"{self.curr_pc:08x} | " + 
                      f"next_pc = {self.pc:08x} | " +
                      f"x{rd} = {self.registers[rd]:08x} | " + 
                      f"mem[?] = {0:08x}")

    @abstractmethod
    def run(self, num_insts):
        """Run the processor. To be implemented by subclasses."""
        pass
