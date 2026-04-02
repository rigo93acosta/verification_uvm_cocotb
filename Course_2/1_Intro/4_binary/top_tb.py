import cocotb
import logging
import random

from cocotb.triggers import Timer
from cocotb.types import LogicArray
from cocotb.types._range import Range

@cocotb.test()
async def test(dut):
    logging.getLogger().setLevel(logging.INFO)
    a = LogicArray(0, 8)
    b = LogicArray(0, 8)
    logging.info(f"Initial values: a={a}, b={b}")
    a[:] = LogicArray.from_signed(random.randint(-5, 5),8)
    b[:] = LogicArray.from_signed(random.randint(-5, 5), 8)
    logging.info(
        f"Random values: a={a.to_signed()}, b={b.to_signed()}"
        )
    a[:] = 0xAA
    b[:] = 0x55
    logging.info(f"Assigned values: a={a}, b={b}")
    a = a.to_signed()
    b = b.to_signed()
    logging.info(f"Signed values: a={str(a)}, b={str(b)}")
    ## Bitwise operations
    a = LogicArray("1011")
    b = LogicArray("1100")
    logging.info(f"a={a}, b={b}")
    logging.info(f"a & b = {a & b}")
    logging.info(f"a | b = {a | b}")
    logging.info(f"a ^ b = {a ^ b}")
    logging.info(f"~a = {~a}")
    ## Shift operations
    a = LogicArray("10110011")
    n = len(a)
    logging.info("Length of a: {}".format(len(a)))
    logging.info(f"a={a}")
    # Desplazar 2 a la izquierda
    val = a.to_unsigned() << 2
    val &= (1 << n) - 1  # Mask to fit within n bits
    a = LogicArray.from_unsigned(val, n)
    logging.info(f"a << 2 = {a}")
    ## Comparisons
    a = LogicArray.from_signed(5, 8)
    b = LogicArray.from_signed(-3, 8)
    logging.info(f"a={a.to_signed()}, b={b.to_signed()}")
    logging.info(f"a == b: {a == b}")
    logging.info(f"a != b: {a != b}")
    
