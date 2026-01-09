import cocotb
from cocotb.triggers import RisingEdge, FallingEdge, Timer, Event
from cocotb.clock import Clock
from cocotb_coverage.crv import Randomized
from cocotb.queue import Queue
from cocotb.utils import get_sim_time


class transaction(Randomized):

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


class generator:

    def __init__(self, queue, event, count):  # Custom Constructor
        self.queue = queue
        self.event = event
        self.count = count  # number of stimuli to apply
        self.event.clear()  # warrant event is clear at start

    async def gen_data(self):  # Main task
        for i in range(self.count):
            t = transaction()
            t.randomize()
            cocotb.log.info(f"[GEN]: a: {t.a} b: {t.b} i: {i}")
            await self.queue.put(t)  # put transaction in queue
            await self.event.wait()  # wait for event from driver
            self.event.clear()

        cocotb.log.info(
            f"[GEN]: Generation Complete - {self.count} transactions generated"
        )

class driver:

    def __init__(self, queue, dut): # Custom Constructor
        self.queue = queue
        self.dut = dut

    async def recv_data(self):  # Main task
        while True:
            temp = transaction()
            temp = await self.queue.get()  # get transaction from queue
            cocotb.log.info(f"[DRV]: a: {temp.a} b: {temp.b}")

            # Apply values to DUT
            self.dut.a.value = temp.a
            self.dut.b.value = temp.b

            await RisingEdge(self.dut.clk)  # wait for clock edge
            await RisingEdge(self.dut.clk)

class monitor:

    def __init__(self, dut, queue):  # Custom Constructor
        self.dut = dut
        self.queue = queue

    async def sample_data(self):  # Main task
        while True:
            temp = transaction()
            await FallingEdge(self.dut.clk)  # wait for clock edge
            await FallingEdge(self.dut.clk)  
            
            temp.a = self.dut.a.value.to_unsigned()
            temp.b = self.dut.b.value.to_unsigned()
            temp.y = self.dut.y.value.to_unsigned()

            await self.queue.put(temp)  # put transaction in queue
            cocotb.log.info(
                f"[MON]: a: {temp.a} b: {temp.b} y: {temp.y} @ : {str(get_sim_time(unit='ns'))}"
                )
            
class scoreboard:

    def __init__(self, queue, event):  # Custom Constructor 
        
        self.queue = queue
        self.event = event

    async def compare_data(self):  # Main task

        while True:
            
            temp = await self.queue.get()  # get transaction from queue

            cocotb.log.info(
                f"[SCO]: a: {temp.a} b: {temp.b} y: {temp.y} @ : {str(get_sim_time(unit='ns'))}"
                )
            
            if (temp.y == (temp.a + temp.b)):
                cocotb.log.info("[SCO]: PASS")
            else:
                cocotb.log.error("[SCO]: FAIL")

            self.event.set()  # Notify generator

@cocotb.test()
async def top_tb(dut):

    # Parameters
    queue1 = Queue()
    queue2 = Queue()
    event = Event()
    gen = generator(queue1, event, count=10)
    drv = driver(queue1, dut)

    mon = monitor(dut, queue2)
    sco = scoreboard(queue2, event)

    
    # Clock Generation
    clock = Clock(dut.clk, 10, unit="ns")  # Create
    cocotb.start_soon(clock.start())  # Start clock

    # Start coroutines
    cocotb.start_soon(gen.gen_data())
    cocotb.start_soon(drv.recv_data())
    cocotb.start_soon(mon.sample_data())
    cocotb.start_soon(sco.compare_data())

    # Wait for some time to let the test run
    await Timer(200, unit="ns")
