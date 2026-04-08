import cocotb
from cocotb.triggers import RisingEdge, ClockCycles, Event, Timer
from cocotb.clock import Clock
from cocotb_coverage.crv import Randomized
from cocotb.queue import Queue
from cocotb.utils import get_sim_time

class transaction(Randomized):
    def __init__(self, wr = 1, rd = 0, din = 0,dout = 0, empty = 0, full = 0):
        Randomized.__init__(self)
        self.wr    = wr
        self.rd    = rd 
        self.din   = din 
        self.dout  = dout
        self.empty = empty
        
        self.add_rand("wr", list(range(2)))
        self.add_rand("rd", list(range(2)))
        self.add_rand("din", list(range(16)))
        # Can't read and write at the same time
        self.add_constraint(lambda rd,wr: rd != wr)
        
    def print_in(self, tag = ""):
        cocotb.log.info(f"{tag} wr: {self.wr} rd: {self.rd} din: {int(self.din)}")
    
    def print_out(self, tag = ""):
        cocotb.log.info(f"{tag} wr: {self.wr} rd: {self.rd} din: {int(self.din)} dout: {int(self.dout)} e: {self.empty} f: {self.full}")    

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
                t.print_in("[GEN]")
                await self.queue.put(t)
                await self.event.wait()
                self.event.clear()

class driver():

    def __init__(self, queue, dut):
        self.queue = queue
        self.dut = dut
        
    async def reset_dut(self):
        self.dut.rst.value = 1
        self.dut.wr.value  = 0
        self.dut.rd.value  = 0
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
            temp.print_in('[DRV]')  
            self.dut.din.value = temp.din
            self.dut.wr.value = temp.wr
            self.dut.rd.value = temp.rd
            
            
            await RisingEdge(self.dut.clk)
            self.dut.wr.value = 0
            self.dut.rd.value = 0
            await RisingEdge(self.dut.clk)

class monitor():
    def __init__(self, dut,queue):
        self.dut   = dut
        self.queue = queue

    async def sample_data(self):
        while True:
            temp = transaction()
            await RisingEdge(self.dut.clk)

            temp.din = self.dut.din.value
            temp.wr = self.dut.wr.value
            temp.rd = self.dut.rd.value

            await RisingEdge(self.dut.clk)
            temp.dout = self.dut.dout.value
            temp.full = self.dut.full.value
            temp.empty = self.dut.empty.value
            
            await self.queue.put(temp)
            temp.print_out("[MON]")

class scoreboard():
    def __init__(self,queue,event):
        self.queue = queue
        self.event = event
        self.arr = list()

    def print_list(self):
        data_str = 'Current FIFO Data : '
        for i in self.arr:
            data_str += f'{i.to_unsigned()} '
        
        cocotb.log.info(data_str)
    
    async def compare_data(self):
        while True:
            temp = await self.queue.get()
            temp.print_out('[SCO]')           
            if(temp.wr == 1):
                cocotb.log.info('Data Stored in FIFO')
                self.arr.append(temp.din)
                self.print_list()
            elif(temp.rd == 1):
                if len(self.arr) == 0 :
                    cocotb.log.info('FIFO is empty')
                elif (temp.dout == self.arr.pop(0)):
                    cocotb.log.info('Test Passed')
                    self.print_list()
                else:
                    cocotb.log.error('Test Failed : Read Data Mismatch')
            else:
                cocotb.log.error('Test Failed : Unexpected input stimulus')
                
            cocotb.log.info('-------------------------------------------')
   
            self.event.set()

@cocotb.test()
async def test(dut):

    # Instantiate queues and event
    queue_drv = Queue()
    queue_mon = Queue()
    event = Event()
    
    # Create objects
    gen = generator(queue_drv, event, 40)
    drv = driver(queue_drv, dut)
    mon = monitor(dut,queue_mon)
    sco = scoreboard(queue_mon,event)
    
    # Start clock
    cocotb.start_soon(Clock(dut.clk, 10, 'ns').start())
    # Reset DUT
    await drv.reset_dut()
    
    # Start coroutines
    cocotb.start_soon(gen.gen_data())
    cocotb.start_soon(drv.recv_data())
    cocotb.start_soon(mon.sample_data())
    cocotb.start_soon(sco.compare_data())

    # Let the test run for a while
    await Timer(820, 'ns')