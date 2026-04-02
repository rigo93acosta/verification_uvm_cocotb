import cocotb
import logging
import random

from cocotb.triggers import Timer
from cocotb.utils import get_sim_time
from cocotb.clock import Clock

async def clk1(dut):
    
    h_time = 10
    l_time = 10

    while True:
        dut.clk1.value = 1
        await Timer(h_time, unit='ns')
        dut.clk1.value = 0
        await Timer(l_time, unit='ns')


async def clk2(dut):
    
    h_time = 10
    l_time = 10
    pshift = 3

    dut.clk2.value = 0
    await Timer(pshift, unit='ns')
    while True:
        dut.clk2.value = 1
        await Timer(h_time, unit='ns')
        dut.clk2.value = 0
        await Timer(l_time, unit='ns')

async def clk3(dut):
    
    freq_normal = 1_000_000_000  # 1 GHz -> 1 ns period
    freq = 100_000_000 # 100 MHz
    pshift = 2
    duty_cycle = 0.6

    ton = (1/freq) * duty_cycle * freq_normal
    toff = (1/freq) * (1 - duty_cycle) * freq_normal
    # toff = (freq_normal / freq) - ton # Equal to above line

    logging.info(f"clk3 ton={ton} toff={toff}")
    dut.clk3.value = 0
    await Timer(pshift, unit='ns')
    while True:
        dut.clk3.value = 1
        await Timer(ton, unit='ns')
        dut.clk3.value = 0
        await Timer(toff, unit='ns')

@cocotb.test() 
async def top_tb(dut):
    """ Testbench for clock generator """

    cocotb.start_soon(clk1(dut))
    cocotb.start_soon(clk2(dut))
    cocotb.start_soon(clk3(dut))
    # Clock generator using cocotb built-in
    cocotb.start_soon(Clock(
        dut.clk, 10, unit='ns').start()
    )

    await Timer(100, unit='ns')