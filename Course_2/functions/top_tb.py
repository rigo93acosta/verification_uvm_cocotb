import cocotb
import logging
import random

from cocotb.triggers import Timer
from cocotb.utils import get_sim_time

#sync functions
def add_stimuli(dut):
    print('applied stimuli @ %0s',str(get_sim_time('ns'))) 
    dut.a.value = 4
    dut.b.value = 5
    print('out of add stimuli @ %0s',str(get_sim_time('ns')))
    
def test_add(dut):
    print('Inside test_add @ %0s',str(get_sim_time('ns')))
    if dut.y.value == (
        dut.a.value.to_unsigned() + dut.b.value.to_unsigned()
        ):
       print('Test Pass @ %0s',str(get_sim_time('ns')))
    else:
       print('Test fail @ %0s',str(get_sim_time('ns')))
    	
#async functions
async def clk1(dut):
    ton = 10 #15/20 = 75%
    toff = 10
    while True:
        dut.clk1.value = 1
        await Timer(ton, 'ns')
        dut.clk1.value = 0
        await Timer(toff, 'ns')
    	  	
async def clk2(dut):
    htime = 10
    ltime = 10
    pshift = 3
    dut.clk2.value = 0
    #await Timer(pshift, 'ns')
    while True:
        dut.clk2.value = 1
        await Timer(htime, 'ns')
        dut.clk2.value = 0
        await Timer(ltime, 'ns')    	

@cocotb.test()
async def test(dut):
      cocotb.start_soon(clk1(dut))
      cocotb.start_soon(clk2(dut))
      
      add_stimuli(dut)
      await Timer(20, 'ns')
      test_add(dut)

      await Timer(200, 'ns')