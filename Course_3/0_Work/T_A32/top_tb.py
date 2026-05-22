import cocotb
import logging

from cocotb.triggers import First, Timer
from cocotb.queue import Queue
from cocotb.utils import get_sim_time


class Producer:
    async def write_data(self, queue, total_data:int, delay=None):
        for i in range(total_data):

            await queue.put({"data": i})
            logging.warning(f"Data sent : {i:02d} "
                         f"Queue size {queue.qsize():02d}")
            if delay is not None:
                await Timer(delay, "ns")


class Consumer:
    async def read_data(self, queue, delay=None):
        while True:
            data_queue = await queue.get()
            data = data_queue["data"]
            logging.warning(f"Data rcvd : {data:02d}")
            logging.warning("-------------------------")
            if delay is not None:
                await Timer(delay, "ns")

@cocotb.test()
async def test(dut):

    p1 = Producer()
    c1 = Consumer()
    queue = Queue(maxsize=2)
    writer = cocotb.start_soon(p1.write_data(queue, 20, 2))
    reader = cocotb.start_soon(c1.read_data(queue, 5))

    await First(writer, reader)
    dut._log.info("=" * 30)
    dut._log.info(f"Producer finished at {get_sim_time('ns')} ns")
    dut._log.info("=" * 30)
    while True:
        await Timer(1, "ns")
        if queue.empty():
            dut._log.info("=" * 30)
            dut._log.info(f"Consumer finished at {get_sim_time('ns')} ns")
            dut._log.info("=" * 30)
            break
    dut._log.info("Test completed")
