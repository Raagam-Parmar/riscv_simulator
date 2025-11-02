"""
# List of supported RISC-V Instructions

| Instruction                   | More Information                   |
|-------------------------------|------------------------------------|
| Register-Register Arithmetic  | src.isa.instructions.reg_reg       |
| Register-Immediate Arithmetic | src.isa.instructions.reg_imm       |
| JALR (Jump and link register) | src.isa.instructions.jalr          |
| Load                          | src.isa.instructions.load          |
| Store                         | src.isa.instructions.store         |
| Branch                        | src.isa.instructions.branch        |
| Upper Immediate               | src.isa.instructions.upper_imm     |
| JAL (Jump and link)           | src.isa.instructions.jal           |
| Miscellaneous Memory          | src.isa.instructions.misc_mem      |
| ZICSR Register-Register       | src.isa.instructions.zicsr_reg_reg |
| ZICSR Register-Immediate      | src.isa.instructions.zicsr_reg_imm |
| Atomic                        | src.isa.instructions.atomic        |

## Register-Register Arithmetic Instructions

```
31                 25 24          20 19          15 14    12 11           7 6             0
+--------------------+--------------+--------------+--------+--------------+--------------+
|       funct7       |     rs2      |     rs1      | funct3 |      rd      |   0110011    |
+--------------------+--------------+--------------+--------+--------------+--------------+
```
See: src.isa.instructions.reg_reg

---

## Register-Immediate Arithmetic Instructions

```
31                                20 19          15 14    12 11           7 6             0
+-----------------------------------+--------------+--------+--------------+--------------+
|             imm[11:0]             |     rs1      | funct3 |      rd      |   0010011    |
+-----------------------------------+--------------+--------+--------------+--------------+
```
See: src.isa.instructions.reg_imm

---

## JALR (Jump and link register) Instruction

```
31                                20 19          15 14    12 11           7 6             0
+-----------------------------------+--------------+--------+--------------+--------------+
|             imm[11:0]             |     rs1      | funct3 |      rd      |   1100111    |
+-----------------------------------+--------------+--------+--------------+--------------+
```
See: src.isa.instructions.jalr

---

## Load Instructions
```
31                                20 19          15 14    12 11           7 6             0
+-----------------------------------+--------------+--------+--------------+--------------+
|             imm[11:0]             |     rs1      | funct3 |      rd      |   0000011    |
+-----------------------------------+--------------+--------+--------------+--------------+
```
See: src.isa.instructions.load


## Store Instructions
```
31                 25 24          20 19          15 14    12 11           7 6             0
+--------------------+--------------+--------------+--------+--------------+--------------+
|     imm[11:5]      |     rs2      |     rs1      | funct3 |   imm[4:0]   |   0100011    |
+--------------------+--------------+--------------+--------+--------------+--------------+
```
See: src.isa.instructions.store

---

## Branch Instructions

```
31                 25 24          20 19          15 14    12 11           7 6             0
+--------------------+--------------+--------------+--------+--------------+--------------+
|    imm[12|10:5]    |     rs2      |     rs1      | funct3 | imm[4:1|11]  |   1100011    |
+--------------------+--------------+--------------+--------+--------------+--------------+
```
See: src.isa.instructions.branch

---

## Upper Immediate Instructions

```
31                                                        12 11           7 6             0
+-----------------------------------------------------------+--------------+--------------+
|                          imm[31:12]                       |      rd      |    opcode    |
+-----------------------------------------------------------+--------------+--------------+
```
See: src.isa.instructions.upper_imm

---

## JAL (Jump and link) Instruction

```
31                                                        12 11           7 6             0
+-----------------------------------------------------------+--------------+--------------+
|                imm[20 | 10:1 | 11 | 19:12]                |      rd      |   1101111    |
+-----------------------------------------------------------+--------------+--------------+
```
See: src.isa.instructions.jal

---

## Miscellaneous Memory Instructions

```
31        28 27       24 23       20 19          15 14    12 11           7 6             0
+-----------+-----------+-----------+--------------+--------+--------------+--------------+
|    fm     |   pred    |   succ    |     rs1      | funct3 | imm[4:1|11]  |   0001111    |
+-----------+-----------+-----------+--------------+--------+--------------+--------------+
```
See: src.isa.instructions.misc_mem

---

## ZICSR Register-Register Instructions

```
31                                20 19          15 14    12 11           7 6             0
+-----------------------------------+--------------+--------+--------------+--------------+
|                csr                |     rs1      | funct3 |      rd      |   1110011    |
+-----------------------------------+--------------+--------+--------------+--------------+
```
See: src.isa.instructions.zicsr_reg_reg

---

## ZICSR Register-Register Instructions

```
31                                20 19          15 14    12 11           7 6             0
+-----------------------------------+--------------+--------+--------------+--------------+
|                csr                |     uimm     | funct3 |      rd      |   1110011    |
+-----------------------------------+--------------+--------+--------------+--------------+
```
See: src.isa.instructions.zicsr_reg_imm

---

## Environment Instructions

```
31                 25 24          20 19          15 14    12 11           7 6             0
+--------------------+--------------+--------------+--------+--------------+--------------+
|       funct7       |     rs2      |     rs1      | funct3 |      rd      |   1110011    |
+--------------------+--------------+--------------+--------+--------------+--------------+
```
See: src.isa.instructions.environment

---

## Atomic Instructions

```
31           27 26 25 24          20 19          15 14    12 11           7 6             0
+--------------+--+--+--------------+--------------+--------+--------------+--------------+
|    funct5    |aq|rl|     rs2      |     rs1      | funct3 |      rd      |   1110011    |
+--------------+--+--+--------------+--------------+--------+--------------+--------------+
```
See: src.isa.instructions.atomic
"""

from typing import Union

from src.isa.instructions.reg_reg import Reg_reg, decode_reg_reg
from src.isa.instructions.reg_imm import Reg_imm, decode_reg_imm
from src.isa.instructions.jalr import Jalr, decode_jalr
from src.isa.instructions.load import Load, decode_load
from src.isa.instructions.store import Store, decode_store
from src.isa.instructions.branch import Branch, decode_branch
from src.isa.instructions.upper_imm import Upper_imm, decode_auipc, decode_lui
from src.isa.instructions.jal import Jal, decode_jal
from src.isa.instructions.misc_mem import Misc_mem, decode_misc_mem
from src.isa.instructions.atomic import Atomic, decode_amo
from src.isa.instructions.environment import Env, decode_env
from src.isa.instructions.zicsr_reg_reg import Zicsr_reg_reg, decode_zicsr_reg_reg
from src.isa.instructions.zicsr_reg_imm import Zicsr_reg_imm, decode_zicsr_reg_imm


Instruction = Union[
    Reg_reg,
    Reg_imm,
    Jalr,
    Load,
    Store,
    Branch,
    Upper_imm,
    Jal,
    Misc_mem,
    Atomic,
    Env,
    Zicsr_reg_reg,
    Zicsr_reg_imm,
]
"""
List of all suppported instructions by the simulation library.
"""
