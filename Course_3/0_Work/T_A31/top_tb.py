import cocotb
import logging

from cocotb.triggers import First, Timer
from cocotb.queue import Queue
from cocotb.utils import get_sim_time


class Producer:
    async def write_data(self, queue, delay=None):
        for i in range(10):

            await queue.put({"data": i, "time": get_sim_time("ns")})
            logging.warning(f"Data sent : {i:02d} "
                         f"Queue size {queue.qsize():02d}")
            if delay is not None:
                await Timer(delay, "ns")


class Consumer:
    async def read_data(self, queue, delay=None):
        while True:
            data_queue = await queue.get()
            if delay is not None:
                await Timer(delay / 2, "ns")

            data = data_queue["data"]
            logging.warning(f"Data rcvd : {data:02d}")
            logging.warning("-------------------------")
            if delay is not None:
                await Timer(delay / 2, "ns")
            
            logging.warning(f"Data read : {data_queue['data']:02d} "
                f"Time in queue {(get_sim_time('ns') - data_queue['time']):.2f} ns")


@cocotb.test()
async def test(dut):

    p1 = Producer()
    c1 = Consumer()
    queue = Queue()
    writer = cocotb.start_soon(p1.write_data(queue, 10))
    reader = cocotb.start_soon(c1.read_data(queue, 10))

    await First(writer, reader)
    dut._log.info("Test completed")
