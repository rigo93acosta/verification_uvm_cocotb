import cocotb
import logging
from cocotb.triggers import Timer

@cocotb.test()
async def test(dut):

    logging.info("Starting sum_test")
    dut.a.value = 5
    dut.b.value = 10
    await Timer(10, unit='ns')
    assert dut.s.value == 15, f"Sum incorrect: {dut.s.value} != 15"
    logging.info("sum_test completed successfully")

