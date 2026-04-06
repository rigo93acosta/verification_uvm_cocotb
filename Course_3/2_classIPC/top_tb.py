import cocotb
from cocotb.triggers import Timer, FallingEdge, RisingEdge, ClockCycles
from cocotb.queue import Queue, QueueEmpty, QueueFull

class produce:
    async def write_data(self, queue: Queue, delay: float):
        for i in range(10):
            
            await queue.put(i)
            cocotb.log.info(f'Data sent: {i}, Queue size: {queue.qsize()}')
            if delay is not None:
                await Timer(delay, unit='ns')

class consumer:
    async def read_data(self, queue: Queue, delay: float):
        while True:

            data = await queue.get()
            # await Timer(5, unit='ns')
            if delay is not None:
                await Timer(delay/2, unit='ns')
            cocotb.log.info(f'Data received: {data}')
            cocotb.log.info('--------------------------')
            # await Timer(5, unit='ns')
            if delay is not None:
                await Timer(delay/2, unit='ns')
            

@cocotb.test()
async def test(dut):

    p1 = produce()
    c1 = consumer()
    queue = Queue(maxsize=3)
    cocotb.start_soon(p1.write_data(queue, 2))
    cocotb.start_soon(c1.read_data(queue, 10))

    await Timer(100, unit='ns')