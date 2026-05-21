import cocotb
import random

from cocotb.triggers import Timer
from cocotb.types import LogicArray


@cocotb.test()
async def test(dut):
    error_count = 0  # Initialize the error count

    for _ in range(30):
        din_bin = LogicArray(random.randint(0, 255), 8)
        sel_bin = LogicArray(random.randint(0, 7), 3)

        dut.din.value = din_bin
        dut.sel.value = sel_bin

        await Timer(10, "ns")

        dout_bin = dut.dout.value

        dut._log.info(f"Input -> din: {din_bin}, sel: {sel_bin}, dout: {dout_bin}")
        dut._log.info(
            f"Expected Output -> dout: {din_bin[sel_bin.to_unsigned()]} -- "
            f"Actual Output -> dout: {dout_bin}"
        )

        if str(din_bin[sel_bin.to_unsigned()]) != str(dout_bin):
            error_count += 1

        await Timer(10, "ns")

    dut._log.info("--------------------------------------------------------")
    if error_count > 0:
        dut._log.error("Number of failed test cases: {error_count}")
    else:
        dut._log.info("All test cases passed")
    dut._log.info("--------------------------------------------------------")
