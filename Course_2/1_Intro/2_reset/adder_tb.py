import cocotb
from cocotb.triggers import Timer


@cocotb.test()
async def test(dut):

    # fixed duration
    # rst = dut.rst
    # rst.value = 1
    # await Timer(50, unit="ns")
    # rst.value = 0
    # await Timer(100, unit="ns")

    # Ver variables and methods of the DUT
    # print(dir(dut))

    # fixed duration rst - 2 pos edges clk
    dut.rst.value = 1
    dut._log.info("Resetting DUT")
    await dut.clk.value_change
    await dut.clk.value_change
    # await Edge(dut.clk) # Deprecated
    dut.rst.value = 0
    dut._log.info("Releasing DUT from reset")
    await dut.clk.rising_edge
    await dut.clk.rising_edge
    dut._log.info("Finished reset sequence")
    await Timer(100, unit="ns")
    dut._log.info("Test complete")
