import cocotb
from cocotb.triggers import Event, Timer
from cocotb_coverage.crv import Randomized
from cocotb.queue import Queue


class Transaction(Randomized):
    def __init__(self):
        Randomized.__init__(self)
        self.a = 0
        self.b = 0
        self.y = 0

        self.add_rand("a", list(range(16)))
        self.add_rand("b", list(range(16)))

    def print_in(self, tag=""):
        cocotb.log.info(f"{tag} a: {self.a:02d} b: {self.b:02d}")

    def print_out(self, tag=""):
        cocotb.log.info(f"{tag} a: {self.a:02d} b: {self.b:02d} y: {self.y:02d}")


class Generator:
    def __init__(self, queue, event, count):
        self.queue = queue
        self.count = count
        self.event = event
        self.event.clear()

    async def gen_data(self):
        for _ in range(self.count):
            t = Transaction()
            t.randomize()
            t.print_in(tag="[GEN]")
            await self.queue.put(t)
            await self.event.wait()
            self.event.clear()


class Driver:
    def __init__(self, dut, queue):
        self.dut = dut
        self.queue = queue

    async def drive_data(self, delay: int = 10):
        while True:
            temp = Transaction()
            temp = await self.queue.get()

            self.dut.a.value = temp.a
            self.dut.b.value = temp.b

            temp.print_in(tag="[DRV]")
            await Timer(delay, unit="ns")


class Monitor:
    def __init__(self, dut, queue):
        self.dut = dut
        self.queue = queue

    async def sample_data(self, delay: int = 10):
        while True:
            await Timer(delay // 2, unit="ns")
            temp = Transaction()

            temp.y = self.dut.y.value.to_unsigned()
            temp.a = self.dut.a.value.to_unsigned()
            temp.b = self.dut.b.value.to_unsigned()

            await Timer(delay // 2, unit="ns")
            await self.queue.put(temp)

            temp.print_out(tag="[MON]")


class Scoreboard:
    def __init__(self, queue, event):
        self.queue = queue
        self.event = event

    async def compare_data(self):
        while True:
            temp = Transaction()
            temp = await self.queue.get()
            temp.print_out(tag="[SCB]")
            a = temp.a
            b = temp.b

            if temp.y == (a * b):
                cocotb.log.info(f"[SCB] PASS: {a:02d} * {b:02d} = {temp.y:02d}")
            else:
                cocotb.log.error(f"[SCB] FAIL: {a:02d} * {b:02d} != {temp.y:02d}")

            cocotb.log.info("==" * 40)

            self.event.set()


@cocotb.test()
@cocotb.parametrize(
    ("num_tests", [10, 50, 100]),
    ("delay", [6, 10, 20]),
)
async def mult_test(dut, num_tests, delay):

    # Instantiate the classes
    queue_drv = Queue()
    queue_mon = Queue()
    event = Event()

    # Parameter: number of tests
    NUM_TESTS = num_tests

    # Create objects
    gen = Generator(queue_drv, event, NUM_TESTS)
    drv = Driver(dut, queue_drv)
    mon = Monitor(dut, queue_mon)
    scb = Scoreboard(queue_mon, event)

    cocotb.start_soon(drv.drive_data(delay=delay))
    cocotb.start_soon(mon.sample_data(delay=delay))
    cocotb.start_soon(scb.compare_data())

    await gen.gen_data()
    while True:
        if queue_drv.empty() and queue_mon.empty():
            cocotb.log.info("All transactions processed")
            break
        await Timer(1, unit="ns")

    cocotb.log.info("Test completed")
