import cocotb
from cocotb.triggers import ClockCycles, Event
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
        self.add_constraint(lambda a, b: a != b)


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
            cocotb.log.info(f"[GEN]: a: {t.a:02d} b: {t.b:02d} i: {i:02d}")
            if t.a == t.b:
                raise RuntimeError("constraint violada: a == b")
            await self.queue.put(t)  # put transaction in queue
            await self.event.wait()  # wait for event from driver
            self.event.clear()

        cocotb.log.info(
            f"[GEN]: Generation Complete - {self.count} transactions generated"
        )


class driver:
    def __init__(self, queue, dut, event):  # Custom Constructor
        self.queue = queue
        self.dut = dut
        self.event = event

    async def send_data(self):  # Main task
        while True:
            temp = transaction()
            temp = await self.queue.get()  # get transaction from queue
            cocotb.log.info(f"[DRV]: a: {temp.a:02d} b: {temp.b:02d}")

            # Notify generator to proceed
            await self.dut.clk.rising_edge
            await self.dut.clk.rising_edge

            # Apply values to DUT
            self.dut.a.value = temp.a
            self.dut.b.value = temp.b

            self.event.set()  # Notify generator


class monitor:
    def __init__(self, dut, queue):  # Custom Constructor
        self.dut = dut
        self.queue = queue

    async def sample_data(self):  # Main task
        while True:
            # Sample on rising edge to align with driver
            await self.dut.clk.falling_edge
            await self.dut.clk.falling_edge

            y_val = self.dut.y.value.to_unsigned()
            cocotb.log.info(f"[MON]: y: {y_val:02d} @ : {str(get_sim_time(unit='ns'))}")
            await self.queue.put(y_val)  # put transaction in queue


class scoreboard:
    def __init__(self, queue):  # Custom Constructor
        self.queue = queue

    async def compare_data(self):  # Main task
        expected = 1
        while True:
            data = await self.queue.get()  # get transaction from queue
            cocotb.log.info(f"[SCO]: y: {data:02d} @ : {str(get_sim_time(unit='ns'))}")
            if data == expected:
                cocotb.log.info(
                    f"[SCO]: Test Passed - Expected: {expected:02d}, Got: {data:02d}"
                )
            else:
                cocotb.log.error(
                    f"[SCO]: Test Failed - Expected: {expected:02d}, Got: {data:02d}"
                )
            expected += 1


@cocotb.test()
async def test(dut):

    # Initialization of queues and events
    stimulus_queue = Queue()
    analysis_queue = Queue()
    handshake_event = Event()
    num_trans = 5

    # Instantiation of components
    gen = generator(stimulus_queue, handshake_event, num_trans)
    drv = driver(stimulus_queue, dut, handshake_event)
    mon = monitor(dut, analysis_queue)
    sco = scoreboard(analysis_queue)

    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    driver_pros = cocotb.start_soon(drv.send_data())
    monitor_procs = cocotb.start_soon(mon.sample_data())
    cocotb.start_soon(sco.compare_data())

    cocotb.log.info("--- Starting Stimulus Generation ---")
    await gen.gen_data()
    cocotb.log.info("--- Stopping Components ---")
    driver_pros.cancel()  # Stopping driver
    monitor_procs.cancel()  # Stopping monitor

    while True:
        if stimulus_queue.empty() and analysis_queue.empty():
            cocotb.log.info("Queues empty, finishing test...")
            break
        await ClockCycles(dut, 2, "ns")

    cocotb.log.info("--- Test Complete ---")
