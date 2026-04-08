import cocotb
from cocotb.triggers import Timer, RisingEdge, FallingEdge, ClockCycles, Event
from cocotb.clock import Clock
from cocotb_coverage.crv import Randomized
from cocotb.queue import Queue
from cocotb.utils import get_sim_time


class transaction(Randomized):
    def __init__(self):
        Randomized.__init__(self)
        self.newd = 0
        self.op = 0
        self.addr = 0
        self.din = 0
        self.dout = 0
        self.busy = 0
        self.ack_err = 0

        self.add_rand("op", [0, 1])  # 0 - write, 1 - read
        self.add_rand("addr", list(range(128)))
        self.add_rand("din", list(range(256)))

        self.add_constraint(lambda addr: addr == 1)
        self.add_constraint(lambda din: din < 50)

    def print_in(self, tag=""):
        print(f"{tag} : op={self.op} addr={self.addr} din={self.din}")

    def print_out(self, tag=""):
        print(
            f"{tag} : op={self.op} addr={self.addr} din={self.din} dout={self.dout}"
        )


class generator:
    def __init__(self, queue, event, count):
        self.queue = queue
        self.event = event
        self.count = count

    async def gen_data(self):
        for i in range(self.count):
            tr = transaction()
            tr.randomize()
            tr.print_in("GEN")
            await self.queue.put(tr)
            await self.event.wait()
            self.event.clear()


class driver:
    def __init__(self, dut, queue):
        self.dut = dut
        self.queue = queue

    async def reset_dut(self):
        self.dut.rst.value = 1
        self.dut.din.value = 0
        self.dut.newd.value = 0
        self.dut.addr.value = 0
        self.dut.op.value = 0
        cocotb.log.info(f"Reset Applied DUT at time {get_sim_time('ns')} ns")
        await ClockCycles(self.dut.clk, 5)
        cocotb.log.info(f"Reset Removed DUT reset at time {get_sim_time('ns')} ns")
        self.dut.rst.value = 0

    async def wr_op(self, tr):
        self.dut.rst.value = 0
        self.dut.newd.value = 1
        self.dut.din.value = tr.din
        self.dut.addr.value = tr.addr
        self.dut.op.value = 0
        tr.print_in("[DRV]")
        await ClockCycles(self.dut.clk, 5)
        self.dut.newd.value = 0
        await RisingEdge(self.dut.done)

    async def rd_op(self, tr):
        self.dut.rst.value = 0
        self.dut.newd.value = 1
        self.dut.din.value = 0
        self.dut.addr.value = tr.addr
        self.dut.op.value = 1
        await ClockCycles(self.dut.clk, 5)
        self.dut.newd.value = 0
        await RisingEdge(self.dut.done)
        tr.dout = self.dut.dout.value
        tr.print_out("[DRV]")

    async def recv_data(self):
        while True:
            temp = transaction()
            temp = await self.queue.get()
            if temp.op == 0:
                await self.wr_op(temp)
            else:
                await self.rd_op(temp)


class monitor:
    def __init__(self, dut, queue):
        self.dut = dut
        self.queue = queue

    async def sample_data(self):
        while True:
            temp = transaction()
            await RisingEdge(self.dut.done)
            temp.din = self.dut.din.value
            temp.op = self.dut.op.value
            temp.addr = self.dut.addr.value
            temp.dout = self.dut.dout.value
            await self.queue.put(temp)
            temp.print_out("[MON]")


class scoreboard:
    def __init__(self, queue, event):
        self.queue = queue
        self.event = event
        self.mem = dict()

        # initialize all the elements to zero
        for i in range(128):
            self.mem.update({i: i})

    async def compare_data(self):
        while True:
            temp = await self.queue.get()
            temp.print_out("[SCO]")
            addr = int(temp.addr)
            din = int(temp.din)
            dout = int(temp.dout)

            if temp.op == 0:
                self.mem.update({addr: din})
                cocotb.log.info("[SCO]: Added new data in mem")
            else:
                dout = self.mem.get(addr)
                if temp.dout == dout:
                    cocotb.log.info(f"[SCO] : TEST PASS {dout}")
                else:
                    cocotb.log.info(f"[SCO] : Test FAIL {dout}")

            cocotb.log.info("-------------------------------------------")

            self.event.set()


@cocotb.test()
async def test_I2C(dut):
    
    

    gen_queue = Queue()
    mon_queue = Queue()
    gen_event = Event()

    gen = generator(gen_queue, gen_event, count=10)
    drv = driver(dut, gen_queue)
    mon = monitor(dut, mon_queue)
    sco = scoreboard(mon_queue, gen_event)

    clk = Clock(dut.clk, 10, unit="ns")
    cocotb.start_soon(clk.start())

    await drv.reset_dut()

    cocotb.start_soon(gen.gen_data())
    cocotb.start_soon(drv.recv_data())
    cocotb.start_soon(mon.sample_data())
    cocotb.start_soon(sco.compare_data())

    await Timer(640000, 'ns')