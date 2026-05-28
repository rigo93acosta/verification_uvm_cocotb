import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, ReadOnly, Event
from cocotb.queue import Queue
from cocotb_coverage.crv import Randomized


class Transaction(Randomized):
    def __init__(self):
        Randomized.__init__(self)
        self.newd = 0
        self.din = 0
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
        cocotb.log.info("============= Resetting DUT       ============")
        await ClockCycles(self.dut.clk, 5)
        cocotb.log.info("============= Releasing DUT reset ============")
        self.dut.rst.value = 0

    async def send_data(self):
        while True:
            temp = Transaction()
            temp = await self.queue.get()
            temp.print_in("[DRV]")
            self.dut.newd.value = 1
            await self.dut.spi_master.sclk.falling_edge
            self.dut.din.value = temp.din
            await self.dut.spi_master.sclk.rising_edge
            self.dut.newd.value = 0
            await self.dut.spi_master.cs.rising_edge


class Monitor:
    def __init__(self, dut, queue):
        self.dut = dut
        self.queue = queue

    async def sample_data(self):
        while True:
            temp = Transaction()
            # Wait for start of operation
            await self.dut.spi_master.cs.falling_edge
            temp.din = self.dut.din.value

            # Sample MOSI on rising edges (data changes on falling edge)
            await self.dut.spi_master.sclk.rising_edge
            dout = 0
            for _ in range(12):
                await self.dut.spi_master.sclk.rising_edge
                await ReadOnly()
                dout = (dout << 1) | int(self.dut.spi_master.mosi.value)

            # Wait for end of operation
            await self.dut.spi_master.cs.rising_edge
            temp.dout = dout
            await self.queue.put(temp)
            cocotb.log.info(
                f"[MON]: din = {int(temp.din):04d} : dout = {int(temp.dout):04d}"
            )


class Scoreboard:
    def __init__(self, queue, event):
        self.queue = queue
        self.event = event

    async def compare_data(self):
        while True:
            temp = Transaction()
            temp = await self.queue.get()
            if temp.din == temp.dout:
                cocotb.log.info(
                    f"[SCO]: din = {int(temp.din):04d} : dout = {int(temp.dout):04d} => PASS"
                )
            else:
                cocotb.log.error(
                    f"[SCO]: din = {int(temp.din):04d} : dout = {int(temp.dout):04d} => FAIL"
                )

            cocotb.log.info("--------------------------------")
            self.event.set()


@cocotb.test()
async def spi_master_slave_test(dut):
    """
    Testbench for SPI Master-Slave communication.
    """

    # Queues and Events
    drv_queue = Queue()
    mon_queue = Queue()
    gen_event = Event()

    n_data = 20
    # Instantiate components
    gen = Generator(drv_queue, gen_event, count=n_data)
    drv = Driver(dut, drv_queue)
    mon = Monitor(dut, mon_queue)
    score = Scoreboard(mon_queue, gen_event)

    # Create clock
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    # Reset DUT
    await drv.reset_dut()

    # Start component coroutines
    driver_process = cocotb.start_soon(drv.send_data())
    monitor_process = cocotb.start_soon(mon.sample_data())
    cocotb.start_soon(score.compare_data())

    await gen.gen_data()  # Wait for generator to finish generating data
    cocotb.log.info("============= Generator finished generating data =============")
    while True:
        if drv_queue.empty() and mon_queue.empty():
            cocotb.log.info("============= All transactions processed         =============")
            break
        await ClockCycles(dut.clk, 1)  # Wait for transactions to be processed

    await ClockCycles(dut.clk, 5)  # Wait for any pending transactions to complete
    driver_process.cancel()
    monitor_process.cancel()

    cocotb.log.info("============= Test completed                     =============")
