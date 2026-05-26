import cocotb
from cocotb.clock import Clock
from cocotb.triggers import Event, ClockCycles, ReadOnly
from cocotb_coverage.crv import Randomized
from cocotb.queue import Queue
import random


class Transaction(Randomized):
    
    def __init__(self, din=0, dout=0):
        Randomized.__init__(self)
        self.din = din
        self.dout = dout

        self.add_rand("din", list(range(2)))  # Assuming 1-bit input
        self.add_constraint(lambda din: din < 2)

class Generator():

    def __init__(self, queue, event, count):
        
        self.queue = queue
        self.event = event
        self.count = count
        self.event.clear()

    async def gen_data(self, seq_random=True):

        seq = [1, 1, 1, 1, 1, 0, 0, 0, 0, 0]
        for i in range(self.count):
            t = Transaction()
            if not seq_random:
                t.din = int(seq[i])
            else:
                t.randomize()

            cocotb.log.info(f"[GEN]: din: {t.din:02d}")
            await self.queue.put(t)
            await self.event.wait()
            self.event.clear()

class Driver():

    def __init__(self, queue, dut):
        self.queue = queue
        self.dut = dut
        
    async def reset_dut(self):
        await self.dut.clk.falling_edge
        self.dut.rst.value = 1
        self.dut.din.value = 0
        self.dut._log.info("---------------- Reset Applied  ----------------")
        await ClockCycles(self.dut.clk,5)
        self.dut._log.info("---------------- Reset Removed  ----------------")
        self.dut._log.info("------------------------------------------------")
        self.dut.rst.value = 0

    async def recv_data(self):
        while True:
            temp = Transaction()
            temp = await self.queue.get()
            self.dut._log.info(f"[DRV]: din: {temp.din:02d}")
              
            await self.dut.clk.falling_edge
            self.dut.din.value = temp.din
            await self.dut.clk.rising_edge

class Monitor():
    def __init__(self, dut,queue):
        self.dut   = dut
        self.queue = queue

    async def sample_data(self):
        while True:
            temp = Transaction()
            await self.dut.clk.rising_edge
            await ReadOnly()
            temp.din = int(self.dut.din.value)
            temp.dout = int(self.dut.dout.value)
            await self.queue.put(temp)
            self.dut._log.info(f"[MON]: din: {temp.din:02d} dout: {temp.dout:02d}")

class Scoreboard():

    def __init__(self,queue,event):

        self.queue = queue
        self.event = event

    async def compare_data(self):
        while True:
            temp = await self.queue.get()           
            cocotb.log.info(f"[SCO]: din: {temp.din:02d} dout: {temp.dout:02d}")
            if(temp.dout == temp.din):
                cocotb.log.info("[SCO]: Test Passed")
            else:
                cocotb.log.error("[SCO]: Test Failed")
            print('-------------------------')
                
            self.event.set()

@cocotb.test()
@cocotb.parametrize(
    ("seq_random", [True, False]),
    )
async def test(dut, seq_random):

    random.seed(42)
    # Instantiate the classes
    queue_drv = Queue()
    queue_mon = Queue()
    event = Event()
    
    # Number of transactions to be generated
    n_events = 10
    
    # Create objects
    gen = Generator(queue_drv, event, n_events)
    drv = Driver(queue_drv, dut)
    mon = Monitor(dut,queue_mon)
    sco = Scoreboard(queue_mon,event)
    

    cocotb.start_soon(Clock(dut.clk, 10, 'ns').start())
    await drv.reset_dut()
    
    driver_process = cocotb.start_soon(drv.recv_data())
    monitor_process = cocotb.start_soon(mon.sample_data())
    cocotb.start_soon(sco.compare_data())

    await gen.gen_data(seq_random)  # Wait for the generator to finish generating transactions
    while True:
        if queue_mon.empty() and queue_drv.empty():
            dut._log.info("All transactions processed.")
            break
        await ClockCycles(dut.clk, 1)
    
    dut._log.info("Stopping driver and monitor processes.")
    driver_process.cancel()
    monitor_process.cancel()

    dut._log.info("Test completed.")
            

    