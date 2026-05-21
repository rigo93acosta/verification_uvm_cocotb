import cocotb
import random
from cocotb.triggers import Timer
from cocotb.utils import get_sim_time


@cocotb.test()
async def test(dut):
    err = 0
    for i in range(10):
        a = random.randint(0, 15)
        b = random.randint(0, 15)
        dut.a.value = a
        dut.b.value = b
        await Timer(10, unit="ns")
        y = dut.y.value.to_unsigned()

        if y == (a + b):
            dut._log.info(
                f"Test Passed: a:{a:02d}, b:{b:02d} and y:{y:02d} @ {get_sim_time(unit='ns')}"
            )
        else:
            dut._log.error(
                f"Test Passed: a:{a:02d}, b:{b:02d} and y:{y:02d} @ {get_sim_time(unit='ns')}"
            )
            err = err + 1
        dut._log.info("---------------------------------------------------------")

    if err > 0:
        dut._log.error(f"Number of failed test cases : {err:02d}")
    else:
        dut._log.info("All the test cases Passed")
