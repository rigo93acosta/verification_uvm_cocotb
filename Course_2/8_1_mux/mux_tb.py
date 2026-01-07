import cocotb
import logging
import random

from cocotb.triggers import Timer
from cocotb.types import LogicArray

	 

@cocotb.test()
async def test(dut):
    error_count = 0  # Initialize the error count
    logging.getLogger().setLevel(logging.INFO)
    
    din_bin   = LogicArray(0, 8)
    sel_bin   = LogicArray(0, 3)
    dout_bin  = LogicArray(0, 1)


    for _ in range(30):
        din = random.randint(0,255)
        sel = random.randint(0, 7)
        din_bin[:] = din
        sel_bin[:] = sel
        
        dut.din.value = din
        dut.sel.value = sel
        
        await Timer(10, 'ns')
        
        dout = dut.dout.value
        dout_bin = dout
        
        print('Input -> din:', din_bin,
              'sel:',sel_bin, 
              'dout:', dout_bin)
        print('Output -> exp_dout:', din_bin[sel],
              'dout:',dout_bin)
        if str(din_bin)[7 - sel] != str(dout_bin):
            error_count += 1
     
        await Timer(10, 'ns')
       
    print('--------------------------------------------------------')
    if error_count > 0:
        logging.error('Number of failed test cases: %d', error_count)
    else:
        logging.info('All test cases passed')
    print('--------------------------------------------------------')