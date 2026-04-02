import cocotb
import logging
import random

from cocotb.triggers import Timer, FallingEdge, ClockCycles, RisingEdge
from cocotb.utils import get_sim_time
from cocotb.clock import Clock

mem_arr = {}

async def rst_stimuli(dut):
    logging.info('Applying reset to DUT @ %0s', str(get_sim_time('ns')))
    for i in range(16):
        mem_arr.update({i:0})    
    dut.rst.value = 1
    await Timer(100, 'ns')
    dut.rst.value = 0
    logging.info('System Reset Done @ %0s', str(get_sim_time('ns')))
    print(mem_arr)
    

async def clk_stimuli(dut):
    while True:
        dut.clk.value = 1
        await Timer(10, 'ns')
        dut.clk.value = 0
        await Timer(10, 'ns')

async def write_data(dut):
    await FallingEdge(dut.rst)
    logging.info('--------------------------------------------------')
    logging.info('Writing Data to Memory')
    logging.info('--------------------------------------------------')
    for i in range(15):
        din = random.randint(0, 255)
        addr = random.randint(0, 15)
        mem_arr.update({addr:din})
        dut.din.value = din
        dut.addr.value = addr
        dut.wr.value = 1
        logging.info('---------addr: %0d,Din : %0d @ %0s---------',addr,din, str(get_sim_time('ns')))
        await ClockCycles(dut.clk, 2)
    dut.wr.value = 0
    print(mem_arr) 
    

async def read_data(dut):
    err = 0
    await FallingEdge(dut.wr)
    logging.info('--------------------------------------------------')
    logging.info('Reading Data from Memory')
    logging.info('--------------------------------------------------')
    for i in range(15):
        addr = random.randint(0, 15)
        dut.addr.value = addr
        dut.wr.value = 0
        await ClockCycles(dut.clk, 2)
        dout = dut.dout.value
        logging.info('---------addr: %0d,Dout : %0d @ %0s---------',addr,dout, str(get_sim_time('ns')))
        if mem_arr.get(addr) != dout  :
           err += 1
        else :
           err = err 
    if err > 0:
         logging.error('Test Failed for %0d test cases',err)
    else:
         logging.info('All Test Cases Passed')        
        

@cocotb.test()
async def test(dut):
    logging.getLogger().setLevel(logging.INFO)

    cocotb.start_soon(rst_stimuli(dut))
    cocotb.start_soon(clk_stimuli(dut))
    cocotb.start_soon(write_data(dut))
    cocotb.start_soon(read_data(dut))
    await Timer(2000,'ns')