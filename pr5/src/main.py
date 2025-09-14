import sys

from ram import RAM
from constants import XWIDTH, BASE_ADDR

ram = RAM(XWIDTH, XWIDTH)

file = sys.argv[1]

with open(file, "rb") as f:
    ram.load(f.read(), BASE_ADDR)


# ram.print_words(0x80002000, 0x80002040)
# ram.print_words(0x80000000, 0x80008020)
