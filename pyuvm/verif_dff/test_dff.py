import cocotb
from cocotb.triggers import RisingEdge, FallingEdge, ReadOnly
from cocotb.clock import Clock
import pyuvm
from pyuvm import *
import random

# --- 1. Sequence Item (Transacción) ---
# Define los datos que queremos enviar o recibir del DFF


class DFFItem(uvm_sequence_item):
    def __init__(self, name="DFFItem"):
        super().__init__(name)
        self.d = 0  # Entrada D
        self.rst = 0  # Entrada Reset
        self.q = 0  # Salida Q (capturada por el monitor)

    def __str__(self):
        return f"rst={self.rst}, d={self.d}, q={self.q}"

    def randomize(self):
        # El reset es raro, 'd' es aleatorio
        self.rst = 1 if random.random() < 0.1 else 0
        self.d = random.randint(0, 1)


# --- 2. Sequence (Secuencia) ---
# Genera una serie de items de secuencia y los envía al secuenciador


class DFFSequence(uvm_sequence):
    async def body(self):
        # 1. Reset inicial
        item = DFFItem("RST_ITEM")
        await self.start_item(item)
        item.rst = 1
        item.d = 0
        await self.finish_item(item)

        # 2. Generar ítems aleatorios
        for _ in range(20):
            item = DFFItem("RAND_ITEM")
            await self.start_item(item)
            item.randomize()
            # Aseguramos que el rst inicial ya pasó
            if _ > 2:
                item.rst = 0
            await self.finish_item(item)


# --- 3. Driver ---
# Recibe items del secuenciador y los "conduce" (drive) a los pines del DUT


class DFFDriver(uvm_driver):
    def build_phase(self):
        # Obtenemos la jerarquía del DUT desde cocotb
        self.dut = cocotb.top

    async def run_phase(self):
        # Inicializar señales
        self.dut.d.value = 0
        self.dut.rst.value = 0

        # Esperar al primer flanco de reloj para sincronizar
        await FallingEdge(self.dut.clk)

        while True:
            # Obtener el siguiente ítem del secuenciador
            item = await self.seq_item_port.get_next_item()

            # Aplicar valores en el flanco descendente para evitar condiciones de carrera
            # (El DUT muestrea en RisingEdge)
            self.dut.rst.value = item.rst
            self.dut.d.value = item.d

            # Esperar a que pase el flanco ascendente (donde el DUT actúa)
            await FallingEdge(self.dut.clk)

            # Avisar que el ítem ha sido procesado
            self.seq_item_port.item_done()


# --- 4. Monitor ---
# Observa los pines del DUT y envía los datos capturados al scoreboard


class DFFMonitor(uvm_monitor):
    def __init__(self, name, parent):
        super().__init__(name, parent)
        # Puerto de análisis para enviar datos fuera del monitor
        self.ap = uvm_analysis_port("ap", self)

    def build_phase(self):
        self.dut = cocotb.top

    async def run_phase(self):
        while True:
            # Muestrear justo antes del flanco ascendente (para capturar D actual)
            await RisingEdge(self.dut.clk)
            # Esperar un tiempo delta para que Q se actualice en la simulación
            await ReadOnly()

            # Capturar el estado actual
            item = DFFItem("MON_ITEM")
            item.rst = int(self.dut.rst.value)
            item.d = int(self.dut.d.value)
            item.q = int(self.dut.q.value)

            # Enviar al scoreboard
            self.ap.write(item)


# --- 5. Scoreboard ---
# Recibe datos del monitor y verifica si la salida Q coincide con la lógica esperada


class DFFScoreboard(uvm_scoreboard):
    def __init__(self, name, parent):
        super().__init__(name, parent)
        # FIFO para recibir datos del monitor de forma asíncrona
        self.fifo = uvm_tlm_analysis_fifo("fifo", self)
        self.ap = uvm_analysis_port("ap", self)
        self.expected_q = 0  # Modelo de referencia interno

    def connect_phase(self):
        self.ap.connect(self.fifo.analysis_export)

    async def run_phase(self):
        while True:
            # Obtener el item capturado por el monitor
            actual_item = await self.fifo.get()

            # --- Modelo de Referencia ---
            # Lógica del DFF: Si rst es 1, Q es 0. Si no, Q es D.
            if actual_item.rst == 1:
                self.expected_q = 0
            else:
                self.expected_q = actual_item.d

            # --- Comparación ---
            if actual_item.q != self.expected_q:
                self.logger.error(f"¡ERROR DE VERIFICACIÓN!")
                self.logger.error(f"  Entradas muestreadas: {actual_item}")
                self.logger.error(
                    f"  Q Esperada: {self.expected_q}, Q Real: {actual_item.q}"
                )
                assert False  # Detener la simulación si falla
            else:
                self.logger.info(f"OK: {actual_item}")


# --- 6. Agent ---
# Encapsula el Secuenciador, Driver y Monitor


class DFFAgent(uvm_agent):
    def build_phase(self):
        self.sequencer = uvm_sequencer("sequencer", self)
        self.driver = DFFDriver("driver", self)
        self.monitor = DFFMonitor("monitor", self)

    def connect_phase(self):
        # Conectar el Driver al Secuenciador
        self.driver.seq_item_port.connect(self.sequencer.seq_item_export)


# --- 7. Environment (Env) ---
# Contiene el agente y el scoreboard


class DFFEnv(uvm_env):
    def build_phase(self):
        self.agent = DFFAgent("agent", self)
        self.scoreboard = DFFScoreboard("scoreboard", self)

    def connect_phase(self):
        # Conectar el Monitor (dentro del agente) al Scoreboard
        self.agent.monitor.ap.connect(self.scoreboard.fifo.analysis_export)


# --- 8. Test ---
# El nivel superior que arranca la secuencia


@pyuvm.test()
class DFFTest(uvm_test):
    def build_phase(self):
        self.env = DFFEnv("env", self)

    async def run_phase(self):
        # Levantar objeción para que la simulación no termine de inmediato
        self.raise_objection()

        # Arrancar el reloj de cocotb (período de 10 unidades de tiempo)
        cocotb.start_soon(Clock(cocotb.top.clk, 10, unit="ns").start())

        # Ejecutar la secuencia
        seq = DFFSequence("seq")
        await seq.start(self.env.agent.sequencer)

        # Bajar objeción para permitir el fin de la simulación
        self.drop_objection()
