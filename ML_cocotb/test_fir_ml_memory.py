import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
from ml_temporal_agent import TemporalMLGuider # Asegúrate de que el archivo se llame así
import matplotlib.pyplot as plt
import numpy as np

# Configuración de la prueba
ITERATIONS = 600           # Cantidad total de ciclos a simular
HISTORY_DEPTH = 3          # Profundidad de memoria (debe coincidir con la lógica del filtro)

@cocotb.test()
async def fir_ml_test(dut):
    """
    Testbench que utiliza Machine Learning con memoria temporal (Sliding Window)
    para encontrar secuencias de entrada que saturen el filtro FIR.
    """
    
    # -----------------------------------------------------------
    # 1. Configuración Inicial del Entorno
    # -----------------------------------------------------------
    dut._log.info("Iniciando Testbench Asistido por ML (Temporal)...")
    
    # Iniciar Reloj (10ns periodo = 100MHz)
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    
    # Instanciar el Agente de ML
    guider = TemporalMLGuider(history_depth=HISTORY_DEPTH)
    
    # Reset del DUT
    dut.rst.value = 1
    dut.data_in.value = 0
    dut.coeff0.value = 0
    dut.coeff1.value = 0
    dut.coeff2.value = 0
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.rst.value = 0
    dut._log.info("Reset completado.")

    # -----------------------------------------------------------
    # 2. Configuración de Coeficientes (Escenario de Prueba)
    # -----------------------------------------------------------
    # Fijamos coeficientes que hacen posible el overflow, pero requieren
    # una secuencia consistente de entradas altas para lograrlo.
    # Umbral de overflow en RTL es > 16000 o < -16000
    current_coeffs = [80, 80, 80] 
    
    dut.coeff0.value = current_coeffs[0]
    dut.coeff1.value = current_coeffs[1]
    dut.coeff2.value = current_coeffs[2]
    
    dut._log.info(f"Coeficientes fijados en: {current_coeffs}")

    # Variables para reportes y gráficos
    history_magnitudes = []
    overflow_count = 0
    max_magnitude_reached = 0

    # -----------------------------------------------------------
    # 3. Bucle Principal de Simulación
    # -----------------------------------------------------------
    for i in range(ITERATIONS):
        
        # A) El Agente ML decide el siguiente estímulo basado en la historia
        next_data_in = guider.get_stimulus(current_coeffs)
        
        # B) Aplicar estímulo al DUT
        dut.data_in.value = int(next_data_in)
        
        # C) Avanzar tiempo (Reloj + Propagación)
        await RisingEdge(dut.clk)
        await Timer(1, unit="ns") # Delta delay para ver la salida estable
        
        # D) Leer resultados del DUT
        # Es vital tratar la salida como signed integer
        try:
            current_out = dut.data_out.value.to_signed()
        except ValueError:
            current_out = 0 # Manejo de X o Z al inicio
            
        is_overflow = 1 if dut.overflow_detected.value == 1 else 0
        magnitude = abs(current_out)
        
        # E) Retroalimentar al Agente (Aprendizaje)
        # Le decimos: "Con la entrada X (y la historia previa que tú guardas), obtuvimos magnitud Y"
        guider.record_result(next_data_in, current_coeffs, magnitude)
        
        # -------------------------------------------------------
        # F) Logging y Estadísticas
        # -------------------------------------------------------
        history_magnitudes.append(magnitude)
        
        if magnitude > max_magnitude_reached:
            max_magnitude_reached = magnitude
            
        if is_overflow:
            overflow_count += 1
            # Logueamos solo los primeros 5 y luego cada 50 overflows para no saturar la terminal
            if overflow_count <= 5 or overflow_count % 50 == 0:
                 dut._log.info(f"[CICLO {i}] OVERFLOW! Val: {current_out} | Input Seq: {list(guider.input_history)}")

        # Log de progreso periódico
        if i % 50 == 0:
             dut._log.info(f"Progreso: {i}/{ITERATIONS} | Max Mag: {max_magnitude_reached} | Overflows: {overflow_count}")

    # -----------------------------------------------------------
    # 4. Reporte Final y Visualización
    # -----------------------------------------------------------
    dut._log.info("=============================================")
    dut._log.info("SIMULACIÓN FINALIZADA")
    dut._log.info(f"Total Ciclos: {ITERATIONS}")
    dut._log.info(f"Total Overflows encontrados: {overflow_count}")
    dut._log.info(f"Magnitud Máxima alcanzada: {max_magnitude_reached}")
    dut._log.info("Generando gráfico de aprendizaje...")

    try:
        plt.figure(figsize=(10, 6))
        plt.plot(history_magnitudes, label='Magnitud de Salida (|data_out|)', color='blue', alpha=0.6)
        
        # Línea de umbral de overflow (16000 según RTL)
        plt.axhline(y=16000, color='r', linestyle='--', label='Umbral Overflow RTL')
        
        # Línea de tendencia (media móvil) para ver el aprendizaje
        window_size = 20
        if len(history_magnitudes) > window_size:
            moving_avg = np.convolve(history_magnitudes, np.ones(window_size)/window_size, mode='valid')
            plt.plot(range(window_size-1, len(history_magnitudes)), moving_avg, color='orange', linewidth=2, label='Tendencia (Media Móvil)')

        plt.title(f"Evolución del Aprendizaje ML (Filtro FIR)\nCoeficientes: {current_coeffs}")
        plt.xlabel("Ciclos de Simulación")
        plt.ylabel("Magnitud Absoluta de Salida")
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        filename = "ml_learning_curve.png"
        plt.savefig(filename)
        dut._log.info(f"Gráfico guardado exitosamente como: {filename}")
        
    except Exception as e:
        dut._log.warning(f"No se pudo generar el gráfico: {e}")