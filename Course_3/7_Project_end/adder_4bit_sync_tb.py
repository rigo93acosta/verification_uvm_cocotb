import cocotb
from cocotb.triggers import ClockCycles, Event, ReadOnly
from cocotb.clock import Clock
from cocotb_coverage.crv import Randomized
from cocotb.queue import Queue


class Transaction(Randomized):
    def __init__(self, a=0, b=0, y=0):
        Randomized.__init__(self)  # Custom Constructor
        self.a = a
        self.b = b
        self.y = y

        # Randomization
        self.add_rand("a", list(range(16)))
        self.add_rand("b", list(range(16)))

        # Constrains
        self.add_constraint(lambda a: a < 10)
        self.add_constraint(lambda b: b < 10)
        self.add_constraint(lambda a, b: a != b)


class Generator:
    def __init__(self, queue, event, count):  # Custom Constructor
        self.queue = queue
        self.event = event
        self.count = count  # number of stimuli to apply
        self.event.clear()  # warrant event is clear at start

    async def gen_data(self):  # Main task
        for _ in range(self.count):
            t = Transaction()
            t.randomize()
            cocotb.log.info(f"[GEN]: a: {t.a:02d} b: {t.b:02d}")
            await self.queue.put(t)  # put transaction in queue
            await self.event.wait()  # wait for event from driver
            self.event.clear()

        cocotb.log.info(
            f"[GEN]: Generation Complete - {self.count} transactions generated"
        )


class Driver:
    def __init__(self, queue, dut):  # Custom Constructor
        self.queue = queue
        self.dut = dut

    async def send_data(self):  # Main task
        while True:
            temp = Transaction()
            temp = await self.queue.get()  # get transaction from queue
            cocotb.log.info(f"[DRV]: a: {temp.a:02d} b: {temp.b:02d}")

            # Apply values to DUT
            await self.dut.clk.falling_edge
            self.dut.a.value = temp.a
            self.dut.b.value = temp.b
            


class Monitor:
    def __init__(self, dut, queue):  # Custom Constructor
        self.dut = dut
        self.queue = queue

    async def sample_data(self):  # Main task
        while True:
            temp = Transaction()
            await self.dut.clk.rising_edge
            await ReadOnly()

            temp.a = self.dut.a.value.to_unsigned()
            temp.b = self.dut.b.value.to_unsigned()
            temp.y = self.dut.y.value.to_unsigned()

            await self.queue.put(temp)  # put transaction in queue
            cocotb.log.info(f"[MON]: a: {temp.a:02d} b: {temp.b:02d} y: {temp.y:02d}")


class Scoreboard:
    def __init__(self, queue, event):  # Custom Constructor

        self.queue = queue
        self.event = event

    async def compare_data(self):  # Main task

        while True:
            temp = await self.queue.get()  # get transaction from queue

            cocotb.log.info(f"[SCO]: a: {temp.a:02d} b: {temp.b:02d} y: {temp.y:02d}")

            if temp.y == (temp.a + temp.b):
                cocotb.log.info("[SCO]: PASS")
            else:
                cocotb.log.error("[SCO]: FAIL")

            self.event.set()  # Notify generator


async def reset_dut(dut, delay: int = 2):
    cocotb.log.info("Resetting DUT")
    dut.clk.falling_edge
    dut.a.value = 0
    dut.b.value = 0
    await ClockCycles(dut.clk, delay)
    dut._log.info("Resetting finished")


@cocotb.test()
async def top_tb(dut):

    # Clock Generation
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    await reset_dut(dut)

    # Parameters
    queue1 = Queue()
    queue2 = Queue()
    event = Event()
    gen = Generator(queue1, event, count=10)
    drv = Driver(queue1, dut)

    mon = Monitor(dut, queue2)
    sco = Scoreboard(queue2, event)

    # Start coroutines

    monitor_proc = cocotb.start_soon(mon.sample_data())
    driver_proc = cocotb.start_soon(drv.send_data())
    cocotb.start_soon(sco.compare_data())

    await gen.gen_data()  # Wait for generator to finish
    cocotb.log.info("Stopping monitor and driver")

    cocotb.log.info("Generator finished, waiting another components to finish")
    while True:
        if queue1.empty() and queue2.empty():
            cocotb.log.info("All queues empty")
            break
        await ClockCycles(dut.clk, 1)
    await ClockCycles(dut.clk, 1)
    monitor_proc.cancel()
    driver_proc.cancel()    

    cocotb.log.info("Test complete")
