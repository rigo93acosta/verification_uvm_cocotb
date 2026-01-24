import cocotb
from cocotb.clock import Clock
from cocotb.triggers import Event, RisingEdge, Timer, ClockCycles
from cocotb_coverage.crv import Randomized
from cocotb.utils import get_sim_time
from cocotb.queue import Queue

class transaction(Randomized):
    
    def __init__(self, din=0, dout=0):
        Randomized.__init__(self)
        self.din = din
        self.dout = dout

        self.add_rand("din", list(range(2)))  # Assuming 1-bit input
        self.add_constraint(lambda din: din < 2)

class generator():

    def __init__(self, queue, event, count):
        
        self.queue = queue
        self.event = event
        self.count = count
        self.event.clear()

    async def gen_data(self):

        for i in range(self.count):
            t = transaction()
            t.randomize()

            cocotb.log.info(f"[GEN]: din: {t.din} @ : {get_sim_time(unit = 'ns')}")
            await self.queue.put(t)
            await self.event.wait()
            self.event.clear()

class driver():

    def __init__(self, queue, dut):
        self.queue = queue
        self.dut = dut
        
    async def reset_dut(self):
        self.dut.rst.value = 1
        self.dut.din.value = 0
        cocotb.log.info(f"--------Reset Applied @ : {get_sim_time(unit = 'ns')} ----------------")
        await ClockCycles(self.dut.clk,5)
        cocotb.log.info(f"--------Reset Removed @ : {get_sim_time(unit = 'ns')} ----------------")
        cocotb.log.info('-------------------------------------------------------------------------------')
        self.dut.rst.value = 0

    async def recv_data(self):
        while True:
            temp = transaction()
            temp = await self.queue.get()
            cocotb.log.info(f"[DRV]: din: {temp.din} @ : {get_sim_time(unit = 'ns')}")
              
            self.dut.din.value = temp.din
            await RisingEdge(self.dut.clk)
            self.dut.din.value = 0 # // Optional: Clear din after clock edge
            await RisingEdge(self.dut.clk)

class monitor():
    def __init__(self, dut,queue):
        self.dut   = dut
        self.queue = queue

    async def sample_data(self):
        while True:
            temp = transaction()
            await RisingEdge(self.dut.clk)
            temp.dout = self.dut.dout.value # // Optional: Sample dout before clock edge
            await RisingEdge(self.dut.clk)
            # temp.dout = self.dut.dout.value # Sample dout after clock edge
            temp.din = self.dut.din.value
            
            
            await self.queue.put(temp)
            cocotb.log.info(f"[MON] din: {temp.din} dout: {temp.dout} @ :{get_sim_time(unit = 'ns')}")

class scoreboard():

    def __init__(self,queue,event):

        self.queue = queue
        self.event = event

    async def compare_data(self):
        while True:
            temp = await self.queue.get()           
            cocotb.log.info(f"[SCO] din: {temp.din} dout: {temp.dout} @ : {get_sim_time(unit = 'ns')}")
            if(temp.dout == temp.din):
                cocotb.log.info("[SCO] : Test Passed")
            else:
                cocotb.log.error("[SCO] : Test Failed")
            print('-------------------------')
                
            self.event.set()

@cocotb.test()
async def test(dut):

    # Instantiate the classes
    queue_drv = Queue()
    queue_mon = Queue()
    event = Event()
    
    # Create objects
    gen = generator(queue_drv, event, 10)
    drv = driver(queue_drv, dut)
    mon = monitor(dut,queue_mon)
    sco = scoreboard(queue_mon,event)
    

    cocotb.start_soon(Clock(dut.clk, 10, 'ns').start())
    await drv.reset_dut()
    
    cocotb.start_soon(gen.gen_data())
    cocotb.start_soon(drv.recv_data())
    cocotb.start_soon(mon.sample_data())
    cocotb.start_soon(sco.compare_data())

    await Timer(200, 'ns')
            

    