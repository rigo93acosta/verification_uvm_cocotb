import cocotb
import random

from cocotb.triggers import Timer
from cocotb.utils import get_sim_time


@cocotb.test()
async def test(dut):
    error_count = 0  # Initialize the error count

    for _ in range(5):
        a = random.randint(0, 15)
        b = random.randint(0, 15)
        cin = random.randint(0, 1)

        dut.a.value = a
        dut.b.value = b
        dut.cin.value = cin

        await Timer(10, "ns")

        sout = dut.sout.value.to_unsigned()
        cout = dut.cout.value

        dut._log.info(f"a: {a:02d} b: {b:02d} cin: {cin:02d} sout: {sout:02d} cout: {int(cout)}")

        if cout == 0:
            if sout != (a + b + cin):
                error_count += 1
                dut._log.info(f"Test Failed @: {get_sim_time(unit='ns')}")
            else:
                dut._log.info(f"Test passed : {sout}, @ {get_sim_time(unit='ns')}")
        else:
            if (sout + 16) != (a + b + cin):
                error_count += 1
                dut._log.info(f"Test Failed @: {get_sim_time(unit='ns')}")
            else:
                dut._log.info(f"Test passed : {sout + 16}, @ {get_sim_time(unit='ns')}")

        await Timer(10, "ns")

    print("--------------------------------------------------------")
    if error_count > 0:
        dut._log.error("Number of failed test cases: {error_count}")
    else:
        dut._log.info("All test cases passed")
    print("--------------------------------------------------------")
