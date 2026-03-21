import cocotb
from cocotb.triggers import RisingEdge, Timer, ReadOnly, NextTimeStep
import pyuvm
from pyuvm import *
import random
import torch
import torch.nn as nn
import torch.optim as optim

# ============================================================
# 🧱 BFM
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

    async def drive(self, op, data=0):
        self.dut.push.value = 0
        self.dut.pop.value = 0

        if op == "push":
            self.dut.push.value = 1
            self.dut.data_in.value = data

        elif op == "pop":
            self.dut.pop.value = 1

        await RisingEdge(self.dut.clk)

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
# 🧠 Q-Network
# ============================================================

class QNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(3, 32),
            nn.ReLU(),
            nn.Linear(32, 32),
            nn.ReLU(),
            nn.Linear(32, 3)
        )

    def forward(self, x):
        return self.net(x)

# ============================================================
# 🤖 RL Agent
# ============================================================

class RLAgent:
    def __init__(self):
        self.qnet = QNet()
        self.optimizer = optim.Adam(self.qnet.parameters(), lr=1e-3)
        self.gamma = 0.9
        self.epsilon = 0.3

    def select_action(self, state):
        if random.random() < self.epsilon:
            return random.randint(0, 2)

        with torch.no_grad():
            s = torch.tensor(state, dtype=torch.float32)
            q = self.qnet(s)
            return torch.argmax(q).item()

    def train_step(self, state, action, reward, next_state):
        s = torch.tensor(state, dtype=torch.float32)
        ns = torch.tensor(next_state, dtype=torch.float32)

        q_values = self.qnet(s)
        q_value = q_values[action]

        with torch.no_grad():
            next_q = torch.max(self.qnet(ns))

        target = reward + self.gamma * next_q
        loss = (q_value - target) ** 2

        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()


# ============================================================
# ✅ SCOREBOARD MODEL (FUENTE DE VERDAD)
# ============================================================

class FifoScoreboardModel:
    def __init__(self, depth=8):
        self.depth = depth
        self.model = []
        self.error_count = 0
        self.sample_count = 0

    def process(self, sample):
        self.sample_count += 1

        req_push = sample["push"]
        req_pop = sample["pop"]

        prev_level = len(self.model)
        was_full = prev_level == self.depth
        was_empty = prev_level == 0

        push_accepted = bool(req_push and not was_full)
        pop_accepted = bool(req_pop and not was_empty)

        if pop_accepted:
            expected = self.model.pop(0)
            actual = sample["data_out"]
            if expected != actual:
                self.error_count += 1

        if push_accepted:
            self.model.append(sample["data_in"])

        expected_full = 1 if len(self.model) == self.depth else 0
        expected_empty = 1 if len(self.model) == 0 else 0

        if sample["full"] != expected_full:
            self.error_count += 1
        if sample["empty"] != expected_empty:
            self.error_count += 1

        return {
            "prev_level": prev_level,
            "new_level": len(self.model),
            "push_accepted": push_accepted,
            "pop_accepted": pop_accepted,
        }

# ============================================================
# 🌍 RL ENV
# ============================================================

class FifoEnvRL:
    def __init__(self, bfm, depth=8):
        self.bfm = bfm
        self.depth = depth
        self.scoreboard = FifoScoreboardModel(depth=depth)

    @property
    def level(self):
        return len(self.scoreboard.model)

    async def reset(self):
        await self.bfm.reset()
        self.scoreboard = FifoScoreboardModel(depth=self.depth)
        return [0, 0, 1]

    async def step(self, action):
        if action == 0:
            op = "push"
        elif action == 1:
            op = "pop"
        else:
            op = "idle"

        data = random.randint(0, 255)

        await self.bfm.drive(op, data)
        sample = await self.bfm.sample()

        transition = self.scoreboard.process(sample)

        prev_level = transition["prev_level"]
        new_level = transition["new_level"]
        push_accepted = transition["push_accepted"]
        pop_accepted = transition["pop_accepted"]

        reward = -0.05

        if new_level == self.depth:
            reward += 1.0
        if new_level == 0:
            reward += 1.0

        if prev_level == self.depth - 1 and new_level == self.depth and push_accepted:
            reward += 2.0
        if prev_level == 1 and new_level == 0 and pop_accepted:
            reward += 2.0

        if not push_accepted and op == "push":
            reward -= 0.2
        if not pop_accepted and op == "pop":
            reward -= 0.2

        level = max(0, min(new_level, self.depth))
        full = sample["full"]
        empty = sample["empty"]

        state = [level, int(full), int(empty)]

        await NextTimeStep()

        return state, reward

# ============================================================
# 🧪 RL TEST
# ============================================================

class FifoRLTest(uvm_test):
    def build_phase(self):
        self.bfm = ConfigDB().get(self, "", "bfm")

    async def run_phase(self):
        self.raise_objection()

        env = FifoEnvRL(self.bfm)
        agent = RLAgent()

        state = await env.reset()

        for step in range(2000):
            action = agent.select_action(state)
            next_state, reward = await env.step(action)

            agent.train_step(state, action, reward, next_state)
            state = next_state

            if step % 200 == 0:
                print(
                    f"[RL] step={step} state={state} reward={reward} "
                    f"sb_errors={env.scoreboard.error_count}"
                )

        if env.scoreboard.error_count > 0:
            raise AssertionError(
                f"RL checker detected {env.scoreboard.error_count} errors "
                f"in {env.scoreboard.sample_count} samples"
            )

        self.drop_objection()

# ============================================================
# 🔌 TOP
# ============================================================

@cocotb.test()
async def run_fifo_rl_test(dut):

    async def clock_gen():
        while True:
            dut.clk.value = 0
            await Timer(5, unit="ns")
            dut.clk.value = 1
            await Timer(5, unit="ns")

    cocotb.start_soon(clock_gen())

    bfm = FifoBFM(dut)
    await bfm.reset()

    ConfigDB().set(None, "*", "bfm", bfm)

    await uvm_root().run_test("FifoRLTest", keep_set={ConfigDB})