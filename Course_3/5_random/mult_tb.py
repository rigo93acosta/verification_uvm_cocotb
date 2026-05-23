import cocotb

from cocotb.triggers import Timer
from cocotb_coverage.crv import Randomized

class transaction(Randomized):
    def __init__(self):
        
        Randomized.__init__(self)
        self.a = 0
        self.b = 0
        self.c = 0

        self.add_rand("a", list(range(16)))
        self.add_rand("b", list(range(16)))
        self.add_rand("c", list(range(16)))


        ## Standalone constraints
        # self.add_constraint(lambda a: a <= 10)
        # self.add_constraint(lambda b: b >= 10)

        # Combined constraint
        self.add_constraint(lambda a, b: a != b)
        self.add_constraint(lambda b, c: b != c)
        self.add_constraint(lambda a, c: a != c)

        # Order of constraints matters
        self.solve_order(["a", "b"], "c")

class transactionB(Randomized):

    def __init__(self):
        
        Randomized.__init__(self)
        self.a = 0
        self.a_range = "low"

        self.add_rand("a", list(range(16)))
        self.add_rand("a_range", ["low", "mid", "high"])

        def a_value(a, a_range):
            if a_range == "low":
                return a < 4
            elif a_range == "mid":
                return 5 <= a <= 10
            elif a_range == "high":
                return 11 <= a <= 15
            
        self.add_constraint(a_value)

class transactionC(Randomized):

    def __init__(self):
        
        Randomized.__init__(self)
        self.b = 0
        self.b_range = 0

        self.add_rand("b", list(range(3)))
        self.add_rand("b_range", list(range(100))) # 10, 80, 10

        def b_value(b, b_range):
            if b_range < 10:
                return b == 0
            elif 10 <= b_range < 90:
                return b == 1
            elif b_range >= 90:
                return b == 2
        
        self.add_constraint(b_value)
        # Forzando el encontrar una solucion en b_range antes que en b
        self.solve_order("b_range", "b")


@cocotb.test()
async def test(dut):

    t = transaction()

    for i in range(10):

        t.randomize()
        # t.randomize_with(lambda a, b: a + b == 4)
        cocotb.log.info(f"Test {i:02d}: a={t.a:02d}, b={t.b:02d}, c={t.c:02d}")
        await Timer(10, unit='ns')
        cocotb.log.info("---------------------")
    
    cocotb.log.info("========================")
    cocotb.log.info("==== Starting TestB ====")
    cocotb.log.info("========================")

    tB = transactionB()

    for i in range(10):

        tB.randomize()
        cocotb.log.info(f"TestB {i:02d}: a={tB.a:02d}, a_range={tB.a_range}")
        await Timer(10, unit='ns')
        cocotb.log.info("---------------------")

    cocotb.log.info("========================")
    cocotb.log.info("==== Starting TestC ====")
    cocotb.log.info("========================")

    tC = transactionC()

    low = 0
    mid = 0
    high = 0

    for i in range(10):

        tC.randomize()
        cocotb.log.info(f"TestC {i:02d}: b={tC.b:02d}, b_range={tC.b_range}")
        await Timer(10, unit='ns')
        cocotb.log.info("---------------------")

        if tC.b_range < 10:
            low += 1
        elif 10 <= tC.b_range < 90:
            mid += 1
        elif tC.b_range >= 90:
            high += 1

    cocotb.log.info(f"Low: {low:02d}, Mid: {mid:02d}, High: {high:02d}")

    