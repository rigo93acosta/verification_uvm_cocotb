import cocotb
import random

from cocotb.triggers import Timer, ReadOnly
from cocotb.utils import get_sim_time
from cocotb.clock import Clock


async def apply_reset(dut):
    dut._log.info(f"Applying reset to DUT @ {get_sim_time('ns')}")
    dut.rst.value = 1
    await Timer(100, "ns")
    dut.rst.value = 0
    dut._log.info(f"System Reset Done @ {get_sim_time('ns')}")


@cocotb.test()
async def test(dut):

    cocotb.start_soon(apply_reset(dut))
    cocotb.start_soon(Clock(dut.clk, 20, "ns").start())

    await Timer(100, "ns")
    dut._log.info(f"Sending Stimuli to DUT @ {get_sim_time('ns')}")
    err = 0
    for i in range(10):
        din = random.randint(0, 1)
        await dut.clk.falling_edge
        dut.din.value = din
        await dut.clk.rising_edge
        await ReadOnly()
        dut._log.info(f"Din: {din:02d} and Dout : {int(dut.dout.value):02d}")
        if dut.dout.value != din:
            err += 1
        else:
            err = err

    if err > 0:
        dut._log.error(
            f"Test Failed for {err} test cases",
        )
    else:
        dut._log.info("All Test Passes")
