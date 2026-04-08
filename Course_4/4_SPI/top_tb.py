import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ClockCycles, Timer, FallingEdge, Event
from cocotb.queue import Queue
from cocotb.utils import get_sim_time
from cocotb_coverage.crv import Randomized

class transaction(Randomized):

    def __init__(self):
        Randomized.__init__(self)
        self.newd = 0
        self.din  = 0
        self.dout = 0

        self.add_rand("din", list(range(4096)))

    def print_in(self, tag=""):
        cocotb.log.info(f"{tag} : din = {self.din}")

class generator():
    def __init__(self, queue, event, count):
        self.queue = queue
        self.event = event
        self.count = count
        self.event.clear()

    async def gen_data(self):
        for i in range(self.count):
            t = transaction()
            t.randomize()
            t.print_in("[GEN]")
            await self.queue.put(t)
            await self.event.wait()
            self.event.clear()

class driver():

    def __init__(self, dut, queue):
        self.dut = dut
        self.queue = queue

    async def reset_dut(self):
        self.dut.rst.value = 1
        self.dut.din.value  = 0
        self.dut.newd.value  = 0
        cocotb.log.info(f"Resetting DUT at time {get_sim_time('ns')} ns")
        await ClockCycles(self.dut.clk, 5)
        cocotb.log.info(f"Releasing DUT reset at time {get_sim_time('ns')} ns")
        self.dut.rst.value = 0

    async def recv_data(self):
        while True:
            temp = transaction()
            temp = await self.queue.get()
            temp.print_in("[DRV]")
            self.dut.din.value = temp.din
            self.dut.newd.value = 1
            await RisingEdge(self.dut.spi_master.sclk) 
            self.dut.newd.value = 0
            await RisingEdge(self.dut.spi_master.cs) # wait for completion of oper

class monitor():

    def __init__(self, dut, queue):
        self.dut = dut
        self.queue = queue

    async def sample_data(self):
        while True:
            temp = transaction()
            # Wait for start of operation
            await FallingEdge(self.dut.spi_master.cs)
            temp.din = self.dut.din.value

            # Sample MOSI on rising edges (data changes on falling edge)
            await RisingEdge(self.dut.spi_master.sclk)
            dout = 0
            for _ in range(12):
                await RisingEdge(self.dut.spi_master.sclk)
                dout = (dout << 1) | int(self.dut.spi_master.mosi.value)

            # Wait for end of operation
            await RisingEdge(self.dut.spi_master.cs)
            temp.dout = dout
            await self.queue.put(temp)
            cocotb.log.info(f"[MON] din: {temp.din} : dout = {temp.dout}")

class scoreboard():

    def __init__(self, queue, event):
        self.queue = queue
        self.event = event

    async def compare_data(self):
        while True:
            temp = transaction()
            temp = await self.queue.get()
            if (temp.din == temp.dout):
                cocotb.log.info(f"[SCORE] PASS: din = {temp.din} dout = {temp.dout}")
            else:
                cocotb.log.error(f"[SCORE] FAIL: din = {temp.din} dout = {temp.dout}")
            
            cocotb.log.info("--------------------------------")
            self.event.set()

@cocotb.test()
async def spi_test(dut):

    cocotb.log.info("Starting SPI Master-Slave Testbench")

    # Queues and Events
    drv_queue = Queue()
    mon_queue = Queue()
    gen_event = Event()

    # Instantiate components
    gen = generator(drv_queue, gen_event, count=5)
    drv = driver(dut, drv_queue)
    mon = monitor(dut, mon_queue)
    score = scoreboard(mon_queue, gen_event)

    # Create clock
    clock = Clock(dut.clk, 10, unit="ns")  #
    cocotb.start_soon(clock.start())  # Start clock

    # Reset DUT
    await drv.reset_dut()

    # Start component coroutines
    cocotb.start_soon(gen.gen_data())
    cocotb.start_soon(drv.recv_data())
    cocotb.start_soon(mon.sample_data())
    cocotb.start_soon(score.compare_data())

    await Timer(15000, unit="ns")

