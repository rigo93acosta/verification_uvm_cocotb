import cocotb
from cocotb.triggers import Timer, RisingEdge, ClockCycles, Event, FallingEdge
from cocotb.clock import Clock
from cocotb_coverage.crv import Randomized
from cocotb.queue import Queue
from cocotb.utils import get_sim_time

class transaction(Randomized):
    
    def __init__(self):
        Randomized.__init__(self)
        self.newd = 0
        self.din  = 0
        self.sclk = 0
        self.mosi = 0
        self.cs   = 1
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
            self.dut.din.value = temp.din #apply newdata
            self.dut.newd.value = 1
            await RisingEdge(self.dut.clk)
            self.dut.newd.value = 0
            await RisingEdge(self.dut.cs) # wait for completion of oper

class monitor():
    def __init__(self, dut, queue):
        self.dut = dut
        self.queue = queue

    async def sample_data(self):
        while True:
            """
            Como envio MSB first no necesito una funcion
            de shift register para reconstruir el dato recibido
            """
            dout = 0 
            temp = transaction()
            await FallingEdge(self.dut.cs) # wait for start of oper
            temp.din = self.dut.din.value
            await RisingEdge(self.dut.sclk) # sync to sclk
            for i in range(12):
                await RisingEdge(self.dut.sclk)
                dout = (dout << 1) | int(self.dut.mosi.value)

            await RisingEdge(self.dut.cs) # wait for end of oper
            temp.dout = dout
            await self.queue.put(temp)
            cocotb.log.info(f"[MON] din: {temp.din.to_unsigned()} : dout = {temp.dout}")
            
class scoreboard():
    def __init__(self, queue, event):
        self.queue = queue
        self.event = event
        self.arr = list()

    async def compare_data(self):

        while True:

            temp = await self.queue.get()
            cocotb.log.info(f"[SCO] din: {temp.din.to_unsigned()} : dout = {temp.dout}")

            if temp.din == temp.dout:
                cocotb.log.info(f"[SCO] Match: din = dout = {temp.din.to_unsigned()}")
            else:
                cocotb.log.error(f"[SCO] Mismatch: din = {temp.din.to_unsigned()} != dout = {temp.dout}")
            
            cocotb.log.info("--------------------------------------------------")
            self.event.set()

@cocotb.test()
async def spi_test(dut):

    cocotb.log.info("Starting SPI UVM-like Testbench")

    # Queues and Events
    drv_queue = Queue()
    mon_queue = Queue()
    gen_event = Event()

    # Instantiate components
    gen = generator(drv_queue, gen_event, count=5)
    drv = driver(dut, drv_queue)
    mon = monitor(dut, mon_queue)
    sco = scoreboard(mon_queue, gen_event)

    # Clock generation
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start()) # 100 MHz clock

    # Reset DUT
    await drv.reset_dut()

    # Start component coroutines
    cocotb.start_soon(gen.gen_data())
    cocotb.start_soon(drv.recv_data())
    cocotb.start_soon(mon.sample_data())
    cocotb.start_soon(sco.compare_data())

    # Wait for all transactions to complete
    await Timer(15000, 'ns')

    cocotb.log.info("SPI UVM-like Testbench Completed")
