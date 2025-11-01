"""
Disassembler for 32-bit RISC-V
Supported extensions: RV32IMA
"""

from src.disassembler.disassembler import disassemble, disassemble_error

__all__ = ["disassemble", "disassemble_error"]
