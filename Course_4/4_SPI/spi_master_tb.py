import cocotb
from cocotb.triggers import ReadOnly, ClockCycles, Event
from cocotb.clock import Clock
from cocotb_coverage.crv import Randomized
from cocotb.queue import Queue


class Transaction(Randomized):
    def __init__(self):
        Randomized.__init__(self)
        self.newd = 0
        self.din = 0
        self.sclk = 0
        self.mosi = 0
        self.cs = 1
        self.dout = 0

        self.add_rand("din", list(range(4096)))

    def print_in(self, tag=""):
        cocotb.log.info(f"{tag}: din = {self.din:04d}")


class Generator:
    def __init__(self, queue, event, count):
        self.queue = queue
        self.event = event
        self.count = count
        self.event.clear()

    async def gen_data(self):
        for i in range(self.count):
            t = Transaction()
            t.randomize()
            t.print_in("[GEN]")
            await self.queue.put(t)
            await self.event.wait()
            self.event.clear()


class Driver:
    def __init__(self, dut, queue):
        self.dut = dut
        self.queue = queue

    async def reset_dut(self):
        self.dut.rst.value = 1
        self.dut.din.value = 0
        self.dut.newd.value = 0
        cocotb.log.info("============== Resetting DUT ==============")
        await ClockCycles(self.dut.clk, 5)
        cocotb.log.info("============== Releasing DUT reset ==============")
        self.dut.rst.value = 0

    async def send_data(self):
        while True:
            temp = Transaction()
            temp = await self.queue.get()
            temp.print_in("[DRV]")
            await self.dut.clk.falling_edge 
            self.dut.din.value = temp.din  # apply newdata
            self.dut.newd.value = 1
            await self.dut.sclk.rising_edge


class Monitor:
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
            temp = Transaction()
            await self.dut.cs.falling_edge  # wait for start of oper
            temp.din = self.dut.din.value
            await self.dut.sclk.rising_edge # sync to sclk (mosi == 0)
            for i in range(12):
                await self.dut.sclk.rising_edge
                await ReadOnly()
                dout = (dout << 1) | int(self.dut.mosi.value)

            await self.dut.cs.rising_edge  # wait for end of oper
            temp.dout = dout
            await self.queue.put(temp)
            cocotb.log.info(
                f"[MON]: din = {temp.din.to_unsigned():04d} : dout = {temp.dout:04d}"
            )


class Scoreboard:
    def __init__(self, queue, event):
        self.queue = queue
        self.event = event
        self.arr = list()

    async def compare_data(self):

        while True:
            temp = await self.queue.get()

            if temp.din == temp.dout:
                cocotb.log.info(
                    f"[SCO]: din = {temp.din.to_unsigned():04d} : dout = "
                    f"{temp.dout:04d} => MATCH"
                )
            else:
                cocotb.log.error(
                    f"[SCO]: Mismatch: din = {temp.din.to_unsigned():04d} != "
                    f"dout = {temp.dout:04d}"
                )

            cocotb.log.info("--------------------------------------------------")
            self.event.set()


@cocotb.test()
async def spi_master(dut):
    """
    SPI UVM-like Testbench in Cocotb
    """

    # Queues and Events
    drv_queue = Queue()
    mon_queue = Queue()
    gen_event = Event()

    n_data = 5
    # Instantiate components
    gen = Generator(drv_queue, gen_event, count=n_data)
    drv = Driver(dut, drv_queue)
    mon = Monitor(dut, mon_queue)
    sco = Scoreboard(mon_queue, gen_event)

    # Clock generation
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())  # 100 MHz clock

    # Reset DUT
    await drv.reset_dut()

    # Start component coroutines
    driver_process = cocotb.start_soon(drv.send_data())
    monitor_process = cocotb.start_soon(mon.sample_data())
    cocotb.start_soon(sco.compare_data())

    await gen.gen_data()  # Wait for generator to finish
    cocotb.log.info("============== Generator finished ==============")
    while True:
        if drv_queue.empty() and mon_queue.empty():
            cocotb.log.info("============== All queues empty ==============")
            break
        await ClockCycles(dut.clk, 1)  # Wait for queues to empty
    
    driver_process.cancel()
    monitor_process.cancel()
    await ClockCycles(dut.clk, 5)  # Allow processes to clean up
    cocotb.log.info("============== Test completed ==============")
