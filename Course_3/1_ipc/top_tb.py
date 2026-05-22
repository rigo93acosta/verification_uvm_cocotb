import cocotb
import logging
import random

from cocotb.triggers import Timer, First
from cocotb.queue import Queue
from cocotb.utils import get_sim_time


async def producer(queue):
    logging.warning(f"Sending Data to Consumer @ {get_sim_time(unit='ns')}")
    for _ in range(10):
        data_i = random.randint(0, 20)
        await queue.put(f"Data -- {data_i}")
        logging.warning(f"Data sent to Consumer ( {data_i} ) @ {get_sim_time(unit='ns')}")
        await Timer(1, unit="ns")


async def consumer(queue):
    logging.warning(f"Receiving Data from Producer @ {get_sim_time(unit='ns')}")
    while True:
        data = await queue.get()
        logging.warning(
            f"Data recv from Producer ( {data} ) @ {get_sim_time(unit='ns')}"
        )
        await Timer(1, unit="ns")


@cocotb.test()
async def test(dut):
    queue = Queue()
    data_prod = cocotb.start_soon(producer(queue))
    data_cons = cocotb.start_soon(consumer(queue))
    
    # Method 1: Wait for a fixed time duration    
    # await Timer(10, "ns")
     
    # Method 2: Wait for the producer to finish sending data
    # await First(data_prod, data_cons)
    # data_cons.cancel()

    # Method 3: Wait for the producer to finish and then check if the consumer is still running
    await data_prod
    if not data_cons.done():
        logging.warning("Consumer is still running, cancelling it.")
        data_cons.cancel()
    else:
        logging.warning("Consumer has already finished.")
