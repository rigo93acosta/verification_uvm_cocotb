import cocotb
import logging
import random

from cocotb.triggers import Timer
from cocotb.utils import get_sim_time

@cocotb.test()
async def test(dut):
    error_count = 0  # Initialize the error count
    logging.getLogger().setLevel(logging.INFO)
    
    a = 0
    b = 0
    cin = 0
    sout = 0
    cout = 0
    
    for _ in range(5):
        a = random.randint(0, 15)
        b = random.randint(0, 15)
        cin = random.randint(0, 1)

        dut.a.value = a
        dut.b.value = b
        dut.cin.value = cin
        
        await Timer(10, 'ns')
        
        sout = dut.sout.value.to_unsigned()
        cout = dut.cout.value
        
        print('a:', a, 'b:', b, 'cin:', cin, 'sout:', sout, 'cout:', cout)
        
        if cout == 0:
            if sout != (a + b + cin):
                error_count += 1
                print('Test Failed @:', str(get_sim_time(unit='ns')))
            else:
                print('Test passed :', sout, '@', str(get_sim_time(unit='ns')))
        else:
            if (sout + 16) != (a + b + cin):
                error_count += 1
                print('Test Failed @:', str(get_sim_time(unit='ns')))
            else:
                print('Test passed :', sout + 16, '@', str(get_sim_time(unit='ns'))) 
                   
        await Timer(10, 'ns')
       
    print('--------------------------------------------------------')
    if error_count > 0:
        logging.error('Number of failed test cases: %d', error_count)
    else:
        logging.info('All test cases passed')
    print('--------------------------------------------------------')