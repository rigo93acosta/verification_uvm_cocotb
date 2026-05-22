import cocotb
import random
from cocotb.triggers import Timer, First, NextTimeStep
from cocotb.queue import Queue


class produce:
    async def write_data(self, queue: Queue, delay: float):
        for _ in range(10):
            data_i = random.randint(0, 100)
            await queue.put(data_i)
            cocotb.log.info(f"Data sent: {data_i:03d}, Queue size: {queue.qsize():03d}")
            if delay is not None:
                await Timer(delay, unit="ns")


class consumer:
    async def read_data(self, queue: Queue, delay: float):
        while True:
            data = await queue.get()
            # await Timer(5, unit='ns')
            if delay is not None:
                await Timer(delay / 2, unit="ns")
            cocotb.log.info(f"Data received: {data:03d}")
            cocotb.log.info("--------------------------")
            # await Timer(5, unit='ns')
            if delay is not None:
                await Timer(delay / 2, unit="ns")


@cocotb.test()
async def test(dut):

    p1 = produce()
    c1 = consumer()
    queue = Queue()
    data_writer = cocotb.start_soon(p1.write_data(queue, 2))
    data_reader = cocotb.start_soon(c1.read_data(queue, 10))

    await First(data_writer, data_reader)
    cocotb.log.info("Producer is done, waiting for consumer to finish...")
    while True:
        await Timer(1, unit="ns")
        if queue.qsize() == 0:
            break
    cocotb.log.info("Consumer is done, test completed.")
