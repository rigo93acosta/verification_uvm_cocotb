import cocotb
import logging

from cocotb.triggers import Timer
from cocotb.queue import Queue, QueueEmpty, QueueFull
from cocotb.utils import get_sim_time

async def producer(queue):
    logging.warning("Sending Data to Consumer @ %0s", str(get_sim_time(unit="ns")))
    for i in range(10):
        await queue.put(f"Data -- {i}")
        logging.warning(
            "Data sent to Consumer   ( %0s ) @ %0s", f"Data -- {i}", str(get_sim_time(unit="ns"))
        )
        await Timer(1, unit="ns")

async def consumer(queue):
    logging.warning("Receiving Data from Producer @ %0s", str(get_sim_time(unit="ns")))
    while True:
        data = await queue.get()
        logging.warning(
            "Data recv from Producer ( %0s ) @ %0s", data, str(get_sim_time(unit="ns"))
        )
        await Timer(1, unit="ns")


@cocotb.test()
async def test(dut):
    queue = Queue()
    cocotb.start_soon(producer(queue))
    cocotb.start_soon(consumer(queue))
    await Timer(10, "ns")
