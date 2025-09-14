def unsigned_min() -> int:
    """Minimum value of unsigned integer, 0"""
    return 0

def unsigned_max(width: int) -> int:
    """Maximum value of unsigned integer which can fit in `width` bits,
    `2^width - 1`
    """
    return 2**width - 1

def signed_min(width: int) -> int:
    """Minimum value of signed integer which can fit in `width` bits,
    `-2^(width - 1)`
    """
    return -2**(width - 1)

def signed_max(width: int) -> int:
    """Maximum value of signed integer which can fit in `width` bits,
    `2^(width - 1) - 1`
    """
    return 2**(width - 1) - 1
