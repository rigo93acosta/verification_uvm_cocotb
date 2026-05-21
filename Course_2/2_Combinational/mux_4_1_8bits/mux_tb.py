import cocotb
import random

from cocotb.triggers import Timer


@cocotb.test()
async def test(dut):
    error_count = 0  # Initialize the error count

    for _ in range(5):
        a = random.randint(0, 255)
        b = random.randint(0, 255)
        c = random.randint(0, 255)
        d = random.randint(0, 255)

        sel = random.randint(0, 3)

        dut.a.value = a
        dut.b.value = b
        dut.c.value = c
        dut.d.value = d

        dut.sel.value = sel

        await Timer(10, "ns")

        dout = dut.dout.value.to_unsigned()

        dut._log.info(f"a: {a:03d} b: {b:03d} c: {c:03d} d: {d:03d} sel: {sel:03d} dout: {dout:03d}")

        if sel == 0 and dout != a:
            error_count += 1
        elif sel == 1 and dout != b:
            error_count += 1
        elif sel == 2 and dout != c:
            error_count += 1
        elif sel == 3 and dout != d:
            error_count += 1
        else:
            error_count = error_count

        await Timer(10, "ns")

    dut._log.info("--------------------------------------------------------")
    if error_count > 0:
        dut._log.error(
            f"Number of failed test cases: {error_count}",
        )
    else:
        dut._log.info("All test cases passed")
    dut._log.info("--------------------------------------------------------")
