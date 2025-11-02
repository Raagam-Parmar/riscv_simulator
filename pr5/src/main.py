import sys

from src.hardware.ram import RAM
from src.utils.constants import XWIDTH, BASE_ADDR, BYTE_WIDTH
from src.disassembler.disassembler import decode_branch
from src.utils.pretty import pp_word
import src.utils.logger as logger


def main():

    loggr = logger.setup()

    ram = RAM(BYTE_WIDTH, XWIDTH, loggr)

    argc = len(sys.argv)

    if argc == 1:
        print("Too few arguments")
    if argc > 2:
        print("Too many arguments")
    if argc != 2:
        print("USAGE: python3 main.py <path/to/.r5ob/file>")
        exit(1)

    file = sys.argv[1]

    n_bytes: int = 0

    with open(file, "rb") as f:
        n_bytes = ram.load(f.read(), BASE_ADDR)

    print("Disassembly of .text (0x80000000)")

    for addr in range(0x80000000, 0x80008000, 4):
        inst = ram.read_word(addr)

        if n_bytes <= 0:
            break

        n_bytes -= 4

        if inst == 0:
            continue

        diss = decode_branch(inst)
        pp_inst = pp_word(inst, BYTE_WIDTH, delimit="")

        if diss:
            print(f"{addr:08x}:\t{pp_inst}          \t{diss}")
        else:
            print(f"{addr:08x}:\t{pp_inst}          unknown")

    print("\n\n.data    (0x80008000)")

    if n_bytes > 0:
        ram.print_words(0x80008000, 0x80008000 + n_bytes - 4, False)


if __name__ == "__main__":
    main()
