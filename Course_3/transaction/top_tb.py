import cocotb
import random

from cocotb.triggers import Timer, RisingEdge, ClockCycles, Event
from cocotb.clock import Clock
from cocotb.queue import Queue

class driver():

    def __init__(self, clk, count):
        self.clk = clk
        self.count = count
        self.queue = Queue()
        self.event = Event()


    async def write(self):
        for i in range(self.count):
            data = random.randint(0, 15)
            cocotb.log.info(f"[WR] : sent new data : {data}")
            await self.queue.put(data)
            await self.event.wait()
            self.event.clear()

    async def read(self):
        while True:
            temp = await self.queue.get()
            await RisingEdge(self.clk)
            cocotb.log.info(f"[RD] : received new data : {temp}")
            cocotb.log.info(f"-----------------------------------")
            self.event.set()

@cocotb.test()
async def test(dut):

    drv = driver(dut.clk, 10)
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    cocotb.start_soon(drv.write())
    cocotb.start_soon(drv.read())

    await Timer(100, unit="ns")