import cocotb
import logging
import random

from cocotb.triggers import Timer
from cocotb.types import LogicArray, Range

def pri_model(input_bin):

    if input_bin[7] == '1':
        exp_val = '111'  
    elif (input_bin)[6] == '1':
        exp_val = '110'
    elif (input_bin)[5] == '1':
        exp_val = '101'
    elif (input_bin)[4] == '1':
        exp_val = '100'
    elif (input_bin)[3] == '1':
        exp_val = '011'
    elif (input_bin)[2] == '1':
        exp_val = '010'
    elif (input_bin)[1] == '1':
        exp_val = '001'
    elif (input_bin)[0] == '1':
        exp_val = '000'
    else:
        exp_val = "000"

    return exp_val


@cocotb.test()
async def test(dut):
    error_count = 0  # Initialize the error count

    for _ in range(15):
        input_rand = LogicArray.from_unsigned(random.randint(0, 255), 8)
        dut.en.value = 1
        dut.i.value = input_rand
        await Timer(10, "ns")
        output_bin = dut.y.value
        dut._log.info(
            f"Input: {input_rand} --"
            f" Output: {output_bin.to_unsigned():03b}"
            f" Expected: {pri_model(input_rand)}"
        )

        if pri_model(input_rand) != str(output_bin):
            error_count += 1
        await Timer(10, "ns")

    print("--------------------------------------------------------")
    if error_count > 0:
        dut._log.error(f"Number of failed test cases: {error_count}")
    else:
        dut._log.info("All test cases passed")
    print("--------------------------------------------------------")

