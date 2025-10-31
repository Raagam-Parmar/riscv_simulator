"""
Disassembler for 32-bit RISC-V
Supported extensions: RV32IMA
"""

from .disassembler import disassemble, disassemble_error

__all__ = ["disassemble", "disassemble_error"]
