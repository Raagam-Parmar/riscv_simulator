"""
# Pretty Printing Utilities
"""


def pp_word(
    word: int,
    width: int,
    delimit: str = " ",
    little_endian: bool = True,
    prefix: str = "0x",
) -> str:
    """Returns pretty printed word (4 bytes, width of one byte is `width`)

    :param word: Word to pretty print
    :param width: Width of one byte (one quarter of a word)
    :param delimit: Delimit symbol after every byte. Defaults to ' '.
    :param little_endian: Print in little endian?. Defaults to True.
    :param prefix: Prefix to be added to the word

    :return: Pretty printed word
    """
    pp: str = ""

    byte_range = range(4)
    byte_range = reversed(range(4)) if little_endian else byte_range

    for i in byte_range:
        byte = (word >> (width * i)) & 0xFF
        pp += f"{byte:02x}{delimit}"

    pp = prefix + pp

    return pp
