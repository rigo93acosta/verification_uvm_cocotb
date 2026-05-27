import cocotb
from cocotb.triggers import ClockCycles, Event, ReadOnly
from cocotb.clock import Clock
from cocotb_coverage.crv import Randomized
from cocotb.queue import Queue
from cocotb.utils import get_sim_time


class Transaction(Randomized):
    def __init__(self, wr=1, rd=0, din=0, dout=0, empty=0, full=0):
        Randomized.__init__(self)
        self.wr = wr
        self.rd = rd
        self.din = din
        self.dout = dout
        self.empty = empty

        self.add_rand("wr", list(range(2)))
        self.add_rand("rd", list(range(2)))
        self.add_rand("din", list(range(16)))
        # Can't read and write at the same time
        self.add_constraint(lambda rd, wr: rd != wr)

    def print_in(self, tag=""):
        cocotb.log.info(
            f"{tag} wr: {self.wr:02d} rd: {self.rd:02d} din: {int(self.din):02d}"
        )

    def print_out(self, tag=""):
        cocotb.log.info(
            f"{tag} wr: {int(self.wr):02d} rd: {int(self.rd):02d} din: {int(self.din):02d} dout: "
            f"{int(self.dout):02d} e: {int(self.empty):02d} f: {int(self.full):02d}"
        )


class Generator:
    def __init__(self, queue, event, count):
        self.queue = queue
        self.event = event
        self.count = count
        self.event.clear()

    async def gen_data(self, test_type: str = "random"):
        for count_i in range(self.count):
            t = Transaction()
            match test_type:
                case "full":
                    t.wr = 1
                    t.rd = 0
                    t.din = count_i % 16
                case "empty":
                    t.wr = 0
                    t.rd = 1
                case "random":
                    t.randomize()
                case "fill_and_empty":
                    is_write = count_i < self.count // 2
                    t.wr = 1 if is_write else 0
                    t.rd = 0 if is_write else 1
                    t.din = count_i % 16 if is_write else t.din
                case _:
                    t.randomize()
            t.print_in("[GEN]")
            await self.queue.put(t)
            await self.event.wait()
            self.event.clear()


class Driver:
    def __init__(self, queue, dut):
        self.queue = queue
        self.dut = dut

    async def reset_dut(self):
        await self.dut.clk.rising_edge
        self.dut.rst.value = 1
        self.dut.wr.value = 0
        self.dut.rd.value = 0
        self.dut.din.value = 0
        cocotb.log.info("---------------- Reset Applied ----------------")
        await ClockCycles(self.dut.clk, 2)
        cocotb.log.info("---------------- Reset Removed ----------------")
        cocotb.log.info(
            "-------------------------------------------------------------------------------"
        )
        self.dut.rst.value = 0

    async def send_data(self):
        while True:
            temp = Transaction()
            temp = await self.queue.get()
            temp.print_in("[DRV]")
            await self.dut.clk.falling_edge
            self.dut.din.value = temp.din
            self.dut.wr.value = temp.wr
            self.dut.rd.value = temp.rd
            await self.dut.clk.rising_edge


class Monitor:
    def __init__(self, dut, queue):
        self.dut = dut
        self.queue = queue

    async def sample_data(self):
        while True:
            temp = Transaction()
            await self.dut.clk.rising_edge
            await ReadOnly()
            temp.din = self.dut.din.value
            temp.wr = self.dut.wr.value
            temp.rd = self.dut.rd.value
            temp.dout = self.dut.dout.value
            temp.full = self.dut.full.value
            temp.empty = self.dut.empty.value

            await self.queue.put(temp)
            temp.print_out("[MON]")


class Scoreboard:
    def __init__(self, queue, event):
        self.queue = queue
        self.event = event
        self.arr = list()

    def print_list(self):
        data_str = "Current FIFO Data : "
        for i in self.arr:
            data_str += f"{i.to_unsigned()} "

        cocotb.log.info(data_str)

    async def compare_data(self):
        while True:
            temp = await self.queue.get()
            temp.print_out("[SCO]")
            if temp.wr == 1:
                cocotb.log.info("Data Stored in FIFO")
                self.arr.append(temp.din)
                self.print_list()
            elif temp.rd == 1:
                if len(self.arr) == 0:
                    cocotb.log.info("FIFO is empty")
                elif temp.dout == self.arr.pop(0):
                    cocotb.log.info("Test Passed")
                    self.print_list()
                else:
                    cocotb.log.error("Test Failed : Read Data Mismatch")
            else:
                cocotb.log.error("Test Failed : Unexpected input stimulus")

            cocotb.log.info("-------------------------------------------")

            self.event.set()


@cocotb.test()
@cocotb.parametrize(
    (
        ("id", "test_type"),
        [
            ("full", "full"),
            ("empty", "empty"),
            ("random", "random"),
            ("fill", "fill_and_empty"),
        ],
    ),
)
async def test(dut, id, test_type):

    dut._log.info(f"Length of memory: {len(dut.mem)}")
    # Instantiate queues and event
    queue_drv = Queue()
    queue_mon = Queue()
    event = Event()

    # Number of transactions to be generated
    match test_type:
        case "full":
            number_of_transactions = len(dut.mem)  # Fill the FIFO to capacity
        case "empty":
            number_of_transactions = 2  # Attempt to read from an empty FIFO
        case "random":
            number_of_transactions = 10
        case "fill_and_empty":
            number_of_transactions = len(dut.mem) * 2  + 1# Fill and then empty
        case _:
            number_of_transactions = 10
    # Create objects
    gen = Generator(queue_drv, event, number_of_transactions)
    drv = Driver(queue_drv, dut)
    mon = Monitor(dut, queue_mon)
    sco = Scoreboard(queue_mon, event)

    # Start clock
    cocotb.start_soon(Clock(dut.clk, 10, "ns").start())
    # Reset DUT
    await drv.reset_dut()

    # Start coroutines
    driver_process = cocotb.start_soon(drv.send_data())
    monitor_process = cocotb.start_soon(mon.sample_data())
    cocotb.start_soon(sco.compare_data())

    await gen.gen_data(test_type)
    while True:
        if queue_drv.empty() and queue_mon.empty():
            dut._log.info("All transactions processed.")
            break
        await ClockCycles(dut.clk, 1)

    dut._log.info("Cancelling driver and monitor processes.")
    driver_process.cancel()
    monitor_process.cancel()

    dut._log.info("Test completed successfully.")
