import cocotb
import logging
import random

from cocotb.triggers import Timer
from cocotb.types import LogicArray

def pri_model(input_bin):

    if str(input_bin)[0] == '1':
        exp_val = '111'  
    elif str(input_bin)[1] == '1':
        exp_val = '110'
    elif str(input_bin)[2] == '1':
        exp_val = '101'
    elif str(input_bin)[3] == '1':
        exp_val = '100'
    elif str(input_bin)[4] == '1':
        exp_val = '011'
    elif str(input_bin)[5] == '1':
        exp_val = '010'
    elif str(input_bin)[6] == '1':
        exp_val = '001'
    elif str(input_bin)[7] == '1':
        exp_val = '000'
    else:
        exp_val = '000'
   
    return exp_val

@cocotb.test()
async def test(dut):
    error_count = 0  # Initialize the error count
    logging.getLogger().setLevel(logging.INFO)
    
    input_bin = LogicArray(0, 8)
    output_bin = LogicArray(0, 3)
    
    for _ in range(30):
    
        input_rand = random.randint(0, 255)
        
        input_bin[:] = input_rand
       
        dut.en.value = 1
        dut.i.value = input_rand
        await Timer(10, 'ns')
        output = dut.y.value.to_unsigned()
        output_bin[:] = output
        
        print('Input:', input_bin, 'Output:', output_bin)
        print('ref_data :', pri_model(input_bin))
        
        if pri_model(input_bin) != output_bin:
            error_count += 1
            
        await Timer(10, 'ns')
       
    print('--------------------------------------------------------')
    if error_count > 0:
        logging.error('Number of failed test cases: %d', error_count)
    else:
        logging.info('All test cases passed')
    print('--------------------------------------------------------')