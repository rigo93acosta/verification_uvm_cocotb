import cocotb
import logging
import random

from cocotb.triggers import RisingEdge, Timer
from cocotb.utils import get_sim_time
from cocotb.clock import Clock


async def apply_reset(dut):
    logging.info("Applying reset to DUT @ %0s", str(get_sim_time("ns")))
    dut.rst.value = 1
    await Timer(100, "ns")
    dut.rst.value = 0
    logging.info("System Reset Done @ %0s", str(get_sim_time("ns")))


@cocotb.test()
async def test(dut):
    logging.getLogger().setLevel(logging.INFO)

    cocotb.start_soon(apply_reset(dut))
    cocotb.start_soon(Clock(dut.clk, 20, "ns").start())

    await Timer(100, "ns")
    logging.info("Sending Stimuli to DUT @ %0s", str(get_sim_time("ns")))
    err = 0
    for i in range(10):
        din = random.randint(0, 1)
        dut.din.value = din
        await dut.clk.rising_edge
        await dut.clk.rising_edge
        logging.info("Din: %0d and Dout : %0d", din, dut.dout.value)
        if dut.dout.value != din:
            err += 1
        else:
            err = err

    if err > 0:
        logging.error("Test Failed for %0d test cases", err)
    else:
        logging.info("All Test Passes")
