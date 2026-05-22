import cocotb
import random

from cocotb.triggers import First, Event, ReadOnly
from cocotb.clock import Clock
from cocotb.queue import Queue


class driver:
    def __init__(self, clk, count):
        self.clk = clk
        self.count = count
        self.queue = Queue()
        self.event = Event()

    async def write(self):
        for _ in range(self.count):
            data = random.randint(0, 15)
            cocotb.log.info(f"[WR] : sent     new data : {data:02d}")
            await self.queue.put(data)
            await self.event.wait()
            self.event.clear()

    async def read(self):
        while True:
            temp = await self.queue.get()
            await self.clk.rising_edge
            await ReadOnly()
            cocotb.log.info(f"[RD] : received new data : {temp:02d}")
            cocotb.log.info("-----------------------------------")
            self.event.set()


@cocotb.test()
async def test(dut):

    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    drv = driver(dut.clk, 10)
    writer = cocotb.start_soon(drv.write())
    reader = cocotb.start_soon(drv.read())

    await First(writer, reader)
    dut._log.info("Test finished")
