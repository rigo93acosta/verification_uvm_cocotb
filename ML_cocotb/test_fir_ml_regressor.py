import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
from ml_agent_regressor import MLGuider as ml_agent_regressor
import matplotlib.pyplot as plt # Para graficar al final

@cocotb.test()
async def fir_ml_test(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    guider = ml_agent_regressor()

    dut.rst.value = 1
    await RisingEdge(dut.clk)
    dut.rst.value = 0
    
    # Historial para graficar
    history_magnitudes = []
    max_magnitude_so_far = 0

    dut._log.info("Iniciando búsqueda guiada por Regresión...")

    for i in range(300):
        stim = guider.get_stimulus()
        
        dut.data_in.value = int(stim[0])
        dut.coeff0.value = int(stim[1])
        dut.coeff1.value = int(stim[2])
        dut.coeff2.value = int(stim[3])

        await RisingEdge(dut.clk)
        await Timer(1, unit="ns")

        # Obtenemos el valor real (signed) y calculamos su magnitud
        current_out = dut.data_out.value.to_signed()
        magnitude = abs(current_out)
        
        # Retroalimentamos con la magnitud, no con el booleano
        guider.record_result(stim, magnitude)
        
        # Tracking para logs
        history_magnitudes.append(magnitude)
        if magnitude > max_magnitude_so_far:
            max_magnitude_so_far = magnitude
            dut._log.info(f"Nuevo máximo encontrado: {magnitude} en ciclo {i}")

        if dut.overflow_detected.value == 1:
            dut._log.info(f"!!! OVERFLOW DETECTADO en ciclo {i} !!! Valor: {current_out}")

    # Visualización simple al terminar (se guarda como imagen)
    try:
        plt.figure()
        plt.plot(history_magnitudes)
        plt.title("Magnitud de Salida del Filtro por Ciclo (ML Guided)")
        plt.xlabel("Iteración")
        plt.ylabel("Abs(Data Out)")
        plt.savefig("verification_progress.png")
        dut._log.info("Gráfico guardado en 'verification_progress.png'")
    except Exception as e:
        dut._log.warning(f"No se pudo graficar: {e}")