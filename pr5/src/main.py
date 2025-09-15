import sys

from ram import RAM
from constants import XWIDTH, BASE_ADDR, BYTE_WIDTH
from disassembler import dis

ram = RAM(BYTE_WIDTH, XWIDTH)

argc = len(sys.argv)

if argc == 1:
    print("Too few arguments")
if argc > 2:
    print("Too many arguments")
if argc != 2:
    print("USAGE: python3 main.py <path/to/.r5ob/file>")
    exit(1)

file = sys.argv[1]

with open(file, "rb") as f:
    ram.load(f.read(), BASE_ADDR)


# ram.print_words(0x80002000, 0x80002044)

for addr in range(0x80000000, 0x80002044, 4):
    # print(bin(ram.read_word(addr)))
    inst = ram.read_word(addr)
    
    if inst == 0:
        continue
    
    diss = dis(inst)
    
    if diss:
        print(f"{addr:08x} \t{inst:08x} \t{diss}")
    else:
        print(f"{addr:08x} \t{inst:08x}")

