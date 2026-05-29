import cocotb
from cocotb.triggers import ClockCycles, Event
from cocotb.clock import Clock
from cocotb_coverage.crv import Randomized
from cocotb.queue import Queue


class Transaction(Randomized):
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
        print(f"{tag} : op={int(self.op):03d} addr={int(self.addr):03d} din={int(self.din):03d}")

    def print_out(self, tag=""):
        print(f"{tag} : op={int(self.op):03d} addr={int(self.addr):03d} din={int(self.din):03d} dout={int(self.dout):03d}")


class Generator:
    def __init__(self, queue, event, count):
        self.queue = queue
        self.event = event
        self.count = count

    async def gen_data(self, dir_random=True):
        
        for i in range(self.count):
            tr = Transaction()
            tr.randomize()
            if not dir_random:
                dir_value = [123, 124, 125, 126, 127]
                if i < 5:
                    tr.op = 0  # write operation
                    tr.addr = dir_value[i]
                else:
                    tr.op = 1  # read operation
                    tr.addr = dir_value[i - 5]
            tr.print_in("[GEN]")
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
        cocotb.log.info("===== Reset Applied DUT =====")
        await ClockCycles(self.dut.clk, 5)
        cocotb.log.info("===== Reset Removed DUT =====")
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
        await self.dut.done.rising_edge

    async def rd_op(self, tr):
        self.dut.rst.value = 0
        self.dut.newd.value = 1
        self.dut.din.value = 0
        self.dut.addr.value = tr.addr
        self.dut.op.value = 1
        await ClockCycles(self.dut.clk, 5)
        self.dut.newd.value = 0
        await self.dut.done.rising_edge
        tr.dout = self.dut.dout.value
        tr.print_out("[DRV]")

    async def recv_data(self):
        while True:
            temp = Transaction()
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
            temp = Transaction()
            await self.dut.done.rising_edge
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
@cocotb.parametrize(
    ("dir_random", [True, False])
)
async def i2c_tb(dut, dir_random):
    """
    Testbench para el módulo I2C.
    """

    gen_queue = Queue()
    mon_queue = Queue()
    gen_event = Event()

    n_data = 10
    gen = Generator(gen_queue, gen_event, count=n_data)
    drv = driver(dut, gen_queue)
    mon = monitor(dut, mon_queue)
    sco = scoreboard(mon_queue, gen_event)

    clk = Clock(dut.clk, 10, unit="ns")
    cocotb.start_soon(clk.start())

    await drv.reset_dut()

    generator_process = cocotb.start_soon(gen.gen_data(dir_random))
    driver_process = cocotb.start_soon(drv.recv_data())
    monitor_process = cocotb.start_soon(mon.sample_data())
    cocotb.start_soon(sco.compare_data())

    await generator_process
    cocotb.log.info("===== Generator process completed =====")
    while True:
        if gen_queue.empty() and mon_queue.empty():
            cocotb.log.info("===== All queues are empty. =====")
            break
        await ClockCycles(dut.clk, 1)

    await ClockCycles(dut.clk, 5)

    cocotb.log.info("===== Cancelling driver and monitor processes =====")
    driver_process.cancel()
    monitor_process.cancel()

    cocotb.log.info("===== Test completed =====")
