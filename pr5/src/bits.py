# Functions to calculate the range of signed and unsigned numbers,
# given the width of the storage unit.

def unsigned_min() -> int:
    """Minimum value of unsigned integer, 0"""
    return 0

def unsigned_max(width: int) -> int:
    """Maximum value of unsigned integer which can fit in `width` bits,
    `2^width - 1`
    """
    return (1 << width) - 1

def signed_min(width: int) -> int:
    """Minimum value of signed integer which can fit in `width` bits,
    `-2^(width - 1)`
    """
    return - (1 << (width - 1))

def signed_max(width: int) -> int:
    """Maximum value of signed integer which can fit in `width` bits,
    `2^(width - 1) - 1`
    """
    return (1 << (width - 1)) - 1


# Exceptions for signed and unsigned overflow and underflow.

class UnsignedUnderflow(Exception):
    def __init__(self, data: int, width: int):
        m = unsigned_min()
        self.message = f"Unsigned {data} less than minimum unsigned value {m} for width {width}."
        
        super().__init__(self.message)


class UnsignedOverflow(Exception):
    def __init__(self, data: int, width: int):
        M = unsigned_max(width)
        self.message = f"Unsigned {data} more than maximum unsigned value {M} for width {width}."
        
        super().__init__(self.message)


class SignedUnderflow(Exception):
    def __init__(self, data: int, width: int):
        m = signed_min(width)
        self.message = f"Signed {data} less than minimum signed value {m} for width {width}."
        
        super().__init__(self.message)


class SignedOverflow(Exception):
    def __init__(self, data: int, width: int):
        M = signed_max(width)
        self.message = f"Signed {data} more than maximum signed value {M} for width {width}."
        
        super().__init__(self.message)


# Functions to verify a number can fit in width bits,
# when represented as unsigned or signed

def verifyUnsigned(data: int, width: int):
    if data < unsigned_min():
        raise UnsignedUnderflow(data, width)
    
    if data > unsigned_max(width):
        raise UnsignedOverflow(data, width)


def verifySigned(data: int, width: int):
    if data < signed_min(width):
        raise SignedUnderflow(data, width)
    
    if data > signed_max(width):
        raise SignedOverflow(data, width)
