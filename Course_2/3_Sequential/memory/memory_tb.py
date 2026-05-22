import cocotb
import random

from cocotb.triggers import Timer, ClockCycles, Combine
from cocotb.utils import get_sim_time
from cocotb.clock import Clock

mem_arr = {}


async def rst_stimuli(dut):
    dut._log.info(f"Applying reset to DUT @ {get_sim_time('ns')}")
    for i in range(16):
        mem_arr.update({i: 0})
    dut.rst.value = 1
    await Timer(100, "ns")
    dut.rst.value = 0
    dut._log.info(f"System Reset Done @ {get_sim_time('ns')}")
    dut._log.info(f"Memoria {mem_arr}")


async def clk_stimuli(dut):
    while True:
        dut.clk.value = 1
        await Timer(10, "ns")
        dut.clk.value = 0
        await Timer(10, "ns")


async def write_data(dut):
    await dut.rst.falling_edge
    dut._log.info("--------------------------------------------------")
    dut._log.info("Writing Data to Memory")
    dut._log.info("--------------------------------------------------")
    for i in range(15):
        din = random.randint(0, 255)
        addr = random.randint(0, 15)
        mem_arr.update({addr: din})
        dut.din.value = din
        dut.addr.value = addr
        dut.wr.value = 1
        dut._log.info(
            f"--------- addr: {addr:02d}, "
            f"Din :  {din:03d} @ "
            f"{get_sim_time('ns'):>04.0f} ---------"
        )
        await ClockCycles(dut.clk, 2)
    dut.wr.value = 0
    
    dut._log.info(f"Memoria {mem_arr}")


async def read_data(dut):
    err = 0
    await dut.wr.falling_edge
    dut._log.info("--------------------------------------------------")
    dut._log.info("Reading Data from Memory")
    dut._log.info("--------------------------------------------------")
    for i in range(15):
        addr = random.randint(0, 15)
        dut.addr.value = addr
        dut.wr.value = 0
        await ClockCycles(dut.clk, 2)
        dout = dut.dout.value
        dut._log.info(
            f"--------- addr: {addr:02d}, "
            f"Dout : {dout.to_unsigned():03d} @ "
            f"{get_sim_time('ns'):>04.0f} ---------"
        )
        if mem_arr.get(addr) != dout:
            err += 1
        else:
            err = err
    if err > 0:
        dut._log.error(f"Test Failed for {err} test cases")
    else:
        dut._log.info("All Test Cases Passed")


@cocotb.test()
async def test(dut):

    reset = cocotb.start_soon(rst_stimuli(dut))
    clock = cocotb.start_soon(clk_stimuli(dut))
    write = cocotb.start_soon(write_data(dut))
    read = cocotb.start_soon(read_data(dut))
    await Combine(reset, write, read)
    clock.cancel()
    dut._log.info("Test Completed")
