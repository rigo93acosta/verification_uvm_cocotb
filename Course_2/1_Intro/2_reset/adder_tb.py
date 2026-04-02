import cocotb
import logging
from cocotb.triggers import Timer, RisingEdge, FallingEdge, Edge


@cocotb.test()
async def test(dut):

    ## fixed duration
    # rst = dut.rst
    # rst.value = 1
    # await Timer(50, unit='ns')
    # rst.value = 0
    # await Timer(100, unit='ns')

    ## Ver variables and methods of the DUT
    # print(dir(dut))

    ## fixed duration rst - 2 pos edges clk
    rst = dut.rst
    rst.value = 1
    dut._log.info("Resetting DUT")
    await Edge(dut.clk)
    await Edge(dut.clk)
    rst.value = 0
    dut._log.info("Releasing DUT from reset")
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut._log.info("Finished reset sequence")
    await Timer(100, unit='ns')
    dut._log.info("Test complete")