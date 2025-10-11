# Pretty printers


def pp_word(
    word: int, width: int, delimit: str = " ", little_endian: bool = True
) -> str:
    """Returns pretty printed word (4 bytes, width of one byte is `width`)

    Args:
        word (int): Word to pretty print
        width (int): Width of one byte (one quarter of a word)
        delimit (str, optional): Delimit symbol after every byte. Defaults to ' '.
        little_endian (bool, optional): Print in little endian?. Defaults to True.

    Returns:
        str: Pretty printed word
    """
    pp: str = ""

    byte_range = range(4)
    byte_range = reversed(range(4)) if little_endian else byte_range

    for i in byte_range:
        byte = (word >> (width * i)) & 0xFF
        pp += f"{byte:02x}{delimit}"

    return pp
