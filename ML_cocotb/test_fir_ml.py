# test_fir_ml.py
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
from ml_agent import MLGuider as ml_guider_classifier

@cocotb.test()
async def fir_ml_test(dut):
    # Generar Reloj
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    guider = ml_guider_classifier()

    # Reset
    dut.rst.value = 1
    await RisingEdge(dut.clk)
    dut.rst.value = 0

    hits = 0
    for i in range(200):
        # El ML sugiere [data_in, c0, c1, c2]
        stim = guider.get_stimulus()
        
        dut.data_in.value = int(stim[0])
        dut.coeff0.value = int(stim[1])
        dut.coeff1.value = int(stim[2])
        dut.coeff2.value = int(stim[3])

        await RisingEdge(dut.clk)
        await Timer(1, unit="ns") # Esperar propagación

        hit = 1 if dut.overflow_detected.value == 1 else 0
        guider.record_result(stim, hit)
        
        if hit: hits += 1
        if i % 20 == 0:
            dut._log.info(f"Ciclo {i:03d} - Total Overflows: {hits:04d}")

    dut._log.info(f"Test finalizado. Overflows totales encontrados: {hits}")