import cocotb
from cocotb.triggers import RisingEdge, Timer, ReadOnly
import logging
import pyuvm
from pyuvm import *
import random

# ============================================================
# 🧱 BFM (INTERFAZ)
# ============================================================

class FifoBFM:
    def __init__(self, dut):
        self.dut = dut

    async def reset(self):
        self.dut.push.value = 0
        self.dut.pop.value = 0
        self.dut.data_in.value = 0

        self.dut.rst_n.value = 0
        for _ in range(5):
            await RisingEdge(self.dut.clk)
        self.dut.rst_n.value = 1
        await RisingEdge(self.dut.clk)

    async def drive(self, tx):
        # default
        self.dut.push.value = 0
        self.dut.pop.value = 0

        if tx.op == "push":
            self.dut.push.value = 1
            self.dut.data_in.value = tx.data

        elif tx.op == "pop":
            self.dut.pop.value = 1

        await RisingEdge(self.dut.clk)

        # limpiar
        self.dut.push.value = 0
        self.dut.pop.value = 0

    async def sample(self):
        req_push = int(self.dut.push.value)
        req_pop = int(self.dut.pop.value)
        req_data_in = int(self.dut.data_in.value)

        await RisingEdge(self.dut.clk)
        await ReadOnly()

        return {
            "push": req_push,
            "pop": req_pop,
            "data_in": req_data_in,
            "data_out": int(self.dut.data_out.value),
            "full": int(self.dut.full.value),
            "empty": int(self.dut.empty.value),
        }

# ============================================================
# 📦 TRANSACTION
# ============================================================

class FifoTransaction(uvm_sequence_item):
    def __init__(self, name="fifo_tx"):
        super().__init__(name)
        self.op = None
        self.data = 0

    def randomize(self):
        self.op = random.choice(["push", "pop", "idle"])
        self.data = random.randint(0, 255)

# ============================================================
# 🎲 SEQUENCE (CRV)
# ============================================================

class FifoRandomSequence(uvm_sequence):
    def _weighted_op(self, level, depth):
        if level <= 0:
            ops = ["push", "idle"]
            weights = [0.90, 0.10]
            return random.choices(ops, weights=weights, k=1)[0]

        if level >= depth:
            ops = ["pop", "idle"]
            weights = [0.90, 0.10]
            return random.choices(ops, weights=weights, k=1)[0]

        if level <= 2:
            ops = ["push", "pop", "idle"]
            weights = [0.70, 0.20, 0.10]
            return random.choices(ops, weights=weights, k=1)[0]

        if level >= (depth - 2):
            ops = ["push", "pop", "idle"]
            weights = [0.20, 0.70, 0.10]
            return random.choices(ops, weights=weights, k=1)[0]

        ops = ["push", "pop", "idle"]
        weights = [0.45, 0.45, 0.10]
        return random.choices(ops, weights=weights, k=1)[0]

    def _next_pattern(self, level, depth):
        if level <= 1:
            modes = ["push_burst", "alternating", "mixed"]
            weights = [0.70, 0.20, 0.10]
        elif level >= (depth - 1):
            modes = ["pop_burst", "alternating", "mixed"]
            weights = [0.70, 0.20, 0.10]
        else:
            modes = ["push_burst", "pop_burst", "alternating", "mixed"]
            weights = [0.25, 0.25, 0.30, 0.20]

        mode = random.choices(modes, weights=weights, k=1)[0]

        if mode == "push_burst":
            return ["push"] * random.randint(4, 12)

        if mode == "pop_burst":
            return ["pop"] * random.randint(4, 12)

        if mode == "alternating":
            length = random.randint(6, 16)
            first = "push" if level <= (depth // 2) else "pop"
            second = "pop" if first == "push" else "push"
            return [first if (index % 2 == 0) else second for index in range(length)]

        return [self._weighted_op(level, depth) for _ in range(random.randint(4, 10))]

    async def body(self):
        depth = 8
        predicted_level = 0
        pattern_ops = []

        warmup_cycles = 3
        total_items = 300

        for _ in range(warmup_cycles):
            tx = FifoTransaction()
            tx.op = "idle"
            tx.data = random.randint(0, 255)
            await self.start_item(tx)
            await self.finish_item(tx)

        for _ in range(total_items - warmup_cycles):
            if not pattern_ops:
                pattern_ops = self._next_pattern(predicted_level, depth)

            op = pattern_ops.pop(0)
            op = self._weighted_op(predicted_level, depth) if op == "idle" else op

            if predicted_level == 0 and op == "pop":
                op = self._weighted_op(predicted_level, depth)
            elif predicted_level == depth and op == "push":
                op = self._weighted_op(predicted_level, depth)

            tx = FifoTransaction()
            tx.op = op
            tx.data = random.randint(0, 255)

            await self.start_item(tx)
            await self.finish_item(tx)

            if tx.op == "push" and predicted_level < depth:
                predicted_level += 1
            elif tx.op == "pop" and predicted_level > 0:
                predicted_level -= 1

# ============================================================
# 🚗 DRIVER
# ============================================================

class FifoDriver(uvm_driver):
    def build_phase(self):
        self.bfm = self.cdb_get("bfm")

    async def run_phase(self):
        while True:
            tx = await self.seq_item_port.get_next_item()
            await self.bfm.drive(tx)
            self.seq_item_port.item_done()

# ============================================================
# 👀 MONITOR
# ============================================================

class FifoMonitor(uvm_component):
    def build_phase(self):
        self.bfm = self.cdb_get("bfm")
        self.ap = uvm_analysis_port("ap", self)

    async def run_phase(self):
        while True:
            sample = await self.bfm.sample()
            self.ap.write(sample)

# ============================================================
# 🧠 SCOREBOARD
# ============================================================

class FifoScoreboard(uvm_subscriber):
    def build_phase(self):
        self.model = []
        self.depth = 8
        self.error_count = 0
        self.sample_count = 0
        self.logger.setLevel(logging.DEBUG)

    def write(self, sample):
        self.sample_count += 1

        req_push = sample["push"]
        req_pop = sample["pop"]

        was_full = len(self.model) == self.depth
        was_empty = len(self.model) == 0

        push_accepted = req_push and not was_full
        pop_accepted = req_pop and not was_empty

        self.logger.info(
            f"SB sample={self.sample_count} level_pre={len(self.model)} "
            f"req_push={req_push} req_pop={req_pop} "
            f"push_ok={int(push_accepted)} pop_ok={int(pop_accepted)} "
            f"din={sample['data_in']} dout={sample['data_out']} "
            f"full={sample['full']} empty={sample['empty']}"
        )

        if pop_accepted:
            expected = self.model.pop(0)
            actual = sample["data_out"]

            if expected != actual:
                self.logger.error(f"Mismatch exp={expected} got={actual}")
                self.error_count += 1

        if push_accepted:
            self.model.append(sample["data_in"])

        # checks flags
        expected_full = 1 if len(self.model) == self.depth else 0
        expected_empty = 1 if len(self.model) == 0 else 0

        if sample["full"] != expected_full:
            self.logger.error("FULL flag incorrect")
            self.error_count += 1

        if sample["empty"] != expected_empty:
            self.logger.error("EMPTY flag incorrect")
            self.error_count += 1

    def report_phase(self):
        self.logger.info(
            f"SB summary: samples={self.sample_count} final_level={len(self.model)} errors={self.error_count}"
        )
        if self.error_count > 0:
            raise AssertionError(f"Scoreboard detected {self.error_count} mismatches/check errors")

# ============================================================
# 🏗️ AGENT
# ============================================================

class FifoAgent(uvm_component):
    def build_phase(self):
        self.driver = FifoDriver("driver", self)
        self.monitor = FifoMonitor("monitor", self)
        self.sequencer = uvm_sequencer("sequencer", self)

    def connect_phase(self):
        self.driver.seq_item_port.connect(self.sequencer.seq_item_export)

# ============================================================
# 🌍 ENV
# ============================================================

class FifoEnv(uvm_env):
    def build_phase(self):
        self.agent = FifoAgent("agent", self)
        self.scoreboard = FifoScoreboard("scoreboard", self)

    def connect_phase(self):
        self.agent.monitor.ap.connect(self.scoreboard.analysis_export)

# ============================================================
# 🧪 TEST
# ============================================================

class FifoTest(uvm_test):
    def build_phase(self):
        self.env = FifoEnv("env", self)

    async def run_phase(self):
        self.raise_objection()

        seq = FifoRandomSequence()
        await seq.start(self.env.agent.sequencer)

        self.drop_objection()

# ============================================================
# 🔌 TOP (COCOTB)
# ============================================================

@cocotb.test()
async def run_fifo_test(dut):

    # ---------------------------
    # Clock
    # ---------------------------
    async def clock_gen():
        while True:
            dut.clk.value = 0
            await Timer(5, unit="ns")
            dut.clk.value = 1
            await Timer(5, unit="ns")

    cocotb.start_soon(clock_gen())

    # ---------------------------
    # BFM + Reset
    # ---------------------------
    bfm = FifoBFM(dut)
    await bfm.reset()

    # ---------------------------
    # ConfigDB
    # ---------------------------
    ConfigDB().set(None, "uvm_test_top.env.agent.driver", "bfm", bfm)
    ConfigDB().set(None, "uvm_test_top.env.agent.monitor", "bfm", bfm)

    # ---------------------------
    # Run test
    # ---------------------------
    await uvm_root().run_test("FifoTest", keep_set={ConfigDB})