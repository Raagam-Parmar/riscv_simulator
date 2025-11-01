"""A module to verify the extracted bit fields form an instruction."""


def verify_bit(bit: int):
    """Verify `bit` is either `0` or `1`"""
    if not (0 <= bit <= 1):
        raise ValueError(f"Invalid bit {bit}")


def verify_2b_align(imm: int):
    """Verify `imm` is even"""
    if not (imm & 0b1 == 0):
        raise ValueError(f"Immediate not 2-byte aligned {imm}")


def verify_reg(reg: int):
    """Verify `reg` is in range `[0, 31]`"""
    if not (0 <= reg <= 31):
        raise ValueError(f"Invalid register x{reg}")


def verify_imm12(imm: int):
    """Verify `imm` is in range `[-2048, 2047]`"""
    if not (-2048 <= imm <= 2047):
        raise ValueError(f"12-bit immediate out of range {imm}")


def verify_imm20(imm: int):
    """Verify `imm` is in range `[-524288, 524287]`"""
    if not (-524288 <= imm <= 524287):
        raise ValueError(f"20-bit immediate out of range {imm}")


def verify_uimm4(imm: int):
    """Verify `imm` is in range `[0, 15]`"""
    if not (0 <= imm <= 15):
        raise ValueError(f"4-bit unsigned immediate out of range {imm}")


def verify_uimm5(imm: int):
    """Verify `imm` is in range `[0, 31]`"""
    if not (0 <= imm <= 31):
        raise ValueError(f"5-bit unsigned immediate out of range {imm}")


def verify_uimm6(imm: int):
    """Verify `imm` is in range `[0, 63]`"""
    if not (0 <= imm <= 63):
        raise ValueError(f"6-bit unsigned immediate out of range {imm}")


def verify_uimm12(imm: int):
    """Verify `imm` is in range `[0, 4095]`"""
    if not (0 <= imm <= 4095):
        raise ValueError(f"12-bit unsigned immediate out of range {imm}")


def verify_uimm20(imm: int):
    """Verify `imm` is in range `[0, 1048575]`"""
    if not (0 <= imm <= 1048575):
        raise ValueError(f"20-bit unsigned immediate out of range {imm}")
