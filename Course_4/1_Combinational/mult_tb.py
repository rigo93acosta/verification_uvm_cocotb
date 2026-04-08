import cocotb
from cocotb.triggers import Event, Timer
from cocotb_coverage.crv import Randomized
from cocotb.queue import Queue

# transaction : data members for each input and output port


class transaction(Randomized):
    def __init__(self):
        Randomized.__init__(self)
        self.a = 0
        self.b = 0
        self.y = 0

        self.add_rand("a", list(range(16)))
        self.add_rand("b", list(range(16)))

    def print_in(self, tag=""):
        cocotb.log.info(f"{tag} a: {(self.a)} b: {(self.b)}")

    def print_out(self, tag=""):
        cocotb.log.info(f"{tag} a: {(self.a)} b: {(self.b)} y: {(self.y)}")


# generator : creates random transactions for DUT


class generator:
    def __init__(self, queue, event, count):
        self.queue = queue
        self.count = count
        self.event = event
        self.event.clear()

    async def gen_data(self):
        for _ in range(self.count):
            t = transaction()
            t.randomize()
            t.print_in(tag="[GEN]")
            await self.queue.put(t)
            await self.event.wait()
            self.event.clear()


# driver : apply random transactions to DUT


class driver:
    def __init__(self, dut, queue):
        self.dut = dut
        self.queue = queue

    async def drive_data(self):
        while True:
            temp = transaction()
            temp = await self.queue.get()

            self.dut.a.value = temp.a
            self.dut.b.value = temp.b

            temp.print_in(tag="[DRV]")
            await Timer(10, unit="ns")


# monitor : collect response of DUT


class monitor:
    def __init__(self, dut, queue):
        self.dut = dut
        self.queue = queue

    async def sample_data(self):
        while True:
            await Timer(5, unit="ns")
            temp = transaction()

            temp.y = int(self.dut.y.value)
            temp.a = int(self.dut.a.value)
            temp.b = int(self.dut.b.value)

            await Timer(5, unit="ns")
            await self.queue.put(temp)

            temp.print_out(tag="[MON]")


# scoreboard : compare with expected data


class scoreboard:
    def __init__(self, queue, event):
        self.queue = queue
        self.event = event

    async def compare_data(self):
        while True:
            temp = transaction()
            temp = await self.queue.get()
            temp.print_out(tag="[SCB]")
            a = temp.a
            b = temp.b
            
            if temp.y == (a * b):
                cocotb.log.info(f"[SCB] PASS: {a} * {b} = {temp.y}")
            else:
                cocotb.log.error(f"[SCB] FAIL: {a} * {b} != {temp.y}")
            
            cocotb.log.info("=="*40)

            self.event.set()


@cocotb.test()
async def mult_test(dut):

    # Instantiate the classes
    queue_drv = Queue()
    queue_mon = Queue()
    event = Event()

    # Parameter: number of tests
    NUM_TESTS = 10

    # Create objects
    gen = generator(queue_drv, event, NUM_TESTS)
    drv = driver(dut, queue_drv)
    mon = monitor(dut, queue_mon)
    scb = scoreboard(queue_mon, event)
       

    cocotb.start_soon(gen.gen_data())
    cocotb.start_soon(drv.drive_data())
    cocotb.start_soon(mon.sample_data())
    cocotb.start_soon(scb.compare_data())

    await Timer(60, unit="ns")