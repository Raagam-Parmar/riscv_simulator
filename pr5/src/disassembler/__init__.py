"""
# 32-bit RISC-V Disassembler

Supported extensions: RV32-ZICSR-IMA
"""

from src.disassembler.disassembler import disassemble, disassemble_error

__all__ = ["disassemble", "disassemble_error"]
