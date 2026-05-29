import os
import cocotb
import random
from cocotb.triggers import ClockCycles, Event, ReadOnly
from cocotb.clock import Clock
from cocotb_coverage.crv import Randomized
from cocotb.queue import Queue


class Transaction(Randomized):
    def __init__(self):
        super().__init__()
        self.newd = 0
        self.oper = 1
        self.tx = 0
        self.rx = 0
        self.dintx = 0
        self.doutrx = 0
        self.donetx = 0
        self.donerx = 0

        self.add_rand("dintx", list(range(256)))
        self.add_rand("oper", [0, 1])  # 0 for RX, 1 for TX


class Generator:
    def __init__(self, queue, event, count):
        self.queue = queue
        self.event = event
        self.count = count
        self.event.clear()

    async def gen_data(self):
        for _ in range(self.count):
            temp = Transaction()
            temp.randomize()
            cocotb.log.info(
                f"Generated transaction: oper={temp.oper:03d}, dintx={temp.dintx:03d}"
            )
            await self.queue.put(temp)
            await self.event.wait()
            self.event.clear()


class Driver:
    def __init__(self, queuegd, queueds, dut):
        self.queuegd = queuegd  # drv and sco
        self.queueds = queueds  # gen and drv

        self.dut = dut
        self.dout = 0
        self.rout = 0
        self.rx = 0

    def reverse_Bits(self, n, nbits=8):

        result = 0
        for i in range(nbits):
            result <<= 1
            result |= n & 1
            n >>= 1
        return result

    async def reset_dut(self):
        self.dut.rst.value = 1
        self.dut.dintx.value = 0
        self.dut.newd.value = 0
        self.dut.rx.value = 1
        cocotb.log.info("========== Reset Applied ==========")
        await ClockCycles(self.dut.clk, 5)
        cocotb.log.info("========== Reset Removed ==========")
        cocotb.log.info(
            "-------------------------------------------------------------------------------"
        )
        self.dut.rst.value = 0

    async def data_tx(self, dintx):
        await self.dut.clk.falling_edge
        self.dut.newd.value = 1
        self.dut.dintx.value = dintx
        await self.dut.uart_tx_inst.uclk.rising_edge
        self.dut.newd.value = 0
        await self.queueds.put(dintx)
        cocotb.log.info(f"[DRV]: Data Transmitted {int(dintx):03d}")
        await self.dut.donetx.rising_edge

    async def data_rx(self):
        await self.dut.uart_rx_inst.uclk.rising_edge
        self.dut.rst.value = 0
        self.dut.newd.value = 0
        self.dut.rx.value = 0
        await self.dut.uart_rx_inst.uclk.rising_edge

        for i in range(8):
            self.rx = random.randint(0, 1)
            self.dout = (self.dout << 1) | self.rx
            await self.dut.clk.falling_edge
            self.dut.rx.value = self.rx
            await self.dut.uart_rx_inst.uclk.rising_edge

        self.rout = self.reverse_Bits(self.dout, 8)
        await self.queueds.put(self.rout)
        cocotb.log.info(f"[DRV]: Data RCVD {int(self.rout):03d}")
        await self.dut.donerx.rising_edge
        self.dut.rx.value = 1

    async def send_data(self):
        while True:
            temp = Transaction()
            temp = await self.queuegd.get()
            dintx = temp.dintx
            if temp.oper == 1:
                await self.data_tx(dintx)
            else:
                await self.data_rx()


class Monitor:
    def __init__(self, dut, queuems):
        self.dut = dut
        self.queuems = queuems
        self.dout = 0
        self.rout = 0

    def reverse_Bits(self, n, no_of_bits):
        result = 0
        for i in range(no_of_bits):
            result <<= 1
            result |= n & 1
            n >>= 1
        return result

    async def sample_data(self):
        while True:
            await self.dut.uart_tx_inst.uclk.rising_edge
            if self.dut.newd.value == 1 and self.dut.rx.value == 1:
                await self.dut.uart_tx_inst.uclk.rising_edge
                for i in range(8):
                    await self.dut.uart_tx_inst.uclk.rising_edge
                    self.dout = (self.dout << 1) | int(self.dut.tx.value)

                self.rout = self.reverse_Bits(self.dout, 8)
                cocotb.log.info(f"[MON]: TX DATA: {int(self.rout):03d}")
                await self.dut.donetx.rising_edge
                await self.dut.uart_tx_inst.uclk.rising_edge
                await self.queuems.put(self.rout)

            elif self.dut.rx.value == 0 and self.dut.newd.value == 0:
                await self.dut.donerx.rising_edge
                await ReadOnly()
                self.rout = int(self.dut.doutrx.value)
                cocotb.log.info(f"[MON]: RX DATA: {int(self.rout):03d}")
                await self.dut.uart_tx_inst.uclk.rising_edge
                await self.queuems.put(self.rout)


class Scoreboard:
    def __init__(self, queuems, queueds, event):
        self.queuems = queuems
        self.queueds = queueds
        self.event = event

    async def compare_data(self):
        while True:
            tempd = await self.queueds.get()
            tempm = await self.queuems.get()
            cocotb.log.info(f"[SCO]: Drv: {int(tempd):03d} Mon:  {int(tempm):03d}")

            if tempd == tempm:
                cocotb.log.info("[SCO]: Data Matched")
            else:
                cocotb.log.info("[SCO]: Data Mismatched")

            cocotb.log.info("-------------------------------------------")

            self.event.set()


def _get_baud_rate():
    return int(os.getenv("BAUD_RATE", "9600"))


@cocotb.test(name=f"test_uart_{_get_baud_rate()}")
async def uart_test_tb(dut):
    cocotb.log.info(f"[TEST]: BAUD_RATE={_get_baud_rate()}")

    queuegd = Queue()
    queueds = Queue()
    queuems = Queue()
    event = Event()

    n_data = 5
    gen = Generator(queuegd, event, n_data)
    drv = Driver(queuegd, queueds, dut)

    mon = Monitor(dut, queuems)
    sco = Scoreboard(queuems, queueds, event)

    cocotb.start_soon(Clock(dut.clk, 10, "ns").start())

    await drv.reset_dut()

    generator_process = cocotb.start_soon(gen.gen_data())
    driver_process = cocotb.start_soon(drv.send_data())
    monitor_process = cocotb.start_soon(mon.sample_data())
    cocotb.start_soon(sco.compare_data())

    await generator_process
    cocotb.log.info("========== All Transactions Generated ==========")
    while True:
        if queueds.empty() and queuems.empty() and queuegd.empty():
            cocotb.log.info("========== All Transactions Processed ==========")
            break
        await ClockCycles(dut.clk, 1)

    await ClockCycles(dut.clk, 5)
    cocotb.log.info("========== Ending Test ==========")
    driver_process.cancel()
    monitor_process.cancel()

    cocotb.log.info("========== Test Completed ==========")
