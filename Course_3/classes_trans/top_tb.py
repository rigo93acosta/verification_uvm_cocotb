
import cocotb
import random

from cocotb.triggers import Timer, RisingEdge, ClockCycles, Event
from cocotb.clock import Clock
from cocotb.queue import Queue

class prod():

    def __init__(self, count, event, queue):
        self.count = count
        self.event = event
        self.queue = queue

    async def write(self):

        for i in range(self.count):
            data = random.randint(0, 15)
            cocotb.log.info(f"[WR] : {self.__class__.__name__.upper()} : sent new data : {data}")
            await self.queue.put(data)
            await self.event.wait()
            self.event.clear()

class cons():

    def __init__(self, clk, event, queue):
        self.clk = clk
        self.event = event
        self.queue = queue

    async def read(self):

        while True:
            temp = await self.queue.get()
            await RisingEdge(self.clk)
            cocotb.log.info(f"[RD] : {self.__class__.__name__.upper()} : received new data : {temp}")
            cocotb.log.info("-----------------------------------")
            self.event.set()

@cocotb.test()
async def test(dut):

    event = Event()
    queue = Queue()

    producer = prod(10, event, queue)
    consumer = cons(dut.clk, event, queue)

    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    cocotb.start_soon(producer.write())
    cocotb.start_soon(consumer.read())

    await Timer(100, unit="ns")