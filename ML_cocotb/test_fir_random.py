"""
Testbench de Verificación Estándar - Estimulación Aleatoria Pura
================================================================

Este testbench implementa un enfoque tradicional de verificación funcional
basado en generación aleatoria pura de estímulos, sin ninguna guía de ML.

Sirve como BASELINE para comparar contra los métodos ML-guided.

Características:
- Estimulación completamente aleatoria
- Mismas métricas que testbenches ML
- Mismo número de iteraciones para comparación justa
- Tracking de overflows y magnitudes máximas
"""

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
import random
import matplotlib.pyplot as plt

# Configuración idéntica a test_fir_ml_memory.py para comparación justa
ITERATIONS = 600


@cocotb.test()
async def fir_random_test(dut):
    """
    Testbench de verificación estándar con estimulación aleatoria pura.
    
    Metodología:
    1. Cada ciclo genera estímulos completamente aleatorios
    2. No hay aprendizaje ni optimización
    3. No hay memoria de resultados pasados
    4. Cobertura puramente probabilística
    """
    
    # -----------------------------------------------------------
    # 1. Configuración Inicial
    # -----------------------------------------------------------
    dut._log.info("="*60)
    dut._log.info("Testbench de Verificación ESTÁNDAR (Random)")
    dut._log.info("="*60)
    
    # Iniciar Reloj (10ns periodo = 100MHz)
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    
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
    # 2. Configuración de Coeficientes
    # -----------------------------------------------------------
    # Usamos los mismos coeficientes que test_fir_ml_memory.py
    # para comparación directa
    current_coeffs = [80, 80, 80]
    
    dut.coeff0.value = current_coeffs[0]
    dut.coeff1.value = current_coeffs[1]
    dut.coeff2.value = current_coeffs[2]
    
    dut._log.info(f"Coeficientes fijados en: {current_coeffs}")
    
    # -----------------------------------------------------------
    # 3. Variables de Tracking
    # -----------------------------------------------------------
    history_magnitudes = []
    overflow_count = 0
    max_magnitude_reached = 0
    first_overflow_cycle = None
    overflow_cycles = []
    
    # Rango de valores posibles para data_in (8 bits con signo)
    MIN_VAL = -128
    MAX_VAL = 127
    
    # -----------------------------------------------------------
    # 4. Bucle Principal: Estimulación Aleatoria Pura
    # -----------------------------------------------------------
    dut._log.info(f"Iniciando {ITERATIONS} iteraciones con estimulación ALEATORIA...")
    dut._log.info("")
    
    for i in range(ITERATIONS):
        
        # A) Generar estímulo COMPLETAMENTE ALEATORIO
        # No hay optimización, no hay aprendizaje, no hay memoria
        random_data_in = random.randint(MIN_VAL, MAX_VAL)
        
        # B) Aplicar estímulo al DUT
        dut.data_in.value = random_data_in
        
        # C) Avanzar tiempo
        await RisingEdge(dut.clk)
        await Timer(1, unit="ns")
        
        # D) Leer resultados
        try:
            current_out = dut.data_out.value.to_signed()
        except ValueError:
            current_out = 0
        
        magnitude = abs(current_out)
        overflow_detected = bool(dut.overflow_detected.value)
        
        # E) Registrar métricas
        history_magnitudes.append(magnitude)
        
        # Tracking de máximo alcanzado
        if magnitude > max_magnitude_reached:
            max_magnitude_reached = magnitude
            dut._log.info(f"[Ciclo {i:3d}] Nuevo máximo: {magnitude:5d} (input={random_data_in:4d})")
        
        # Tracking de overflows
        if overflow_detected:
            overflow_count += 1
            overflow_cycles.append(i)
            
            # Registrar primer overflow
            if first_overflow_cycle is None:
                first_overflow_cycle = i
                dut._log.info("")
                dut._log.info("!"*60)
                dut._log.info(f"  PRIMER OVERFLOW detectado en ciclo {i}")
                dut._log.info(f"  Valor: {current_out}, Magnitud: {magnitude}")
                dut._log.info(f"  Input que lo causó: {random_data_in}")
                dut._log.info("!"*60)
                dut._log.info("")
            
            # Logging periódico de overflows
            elif overflow_count <= 5 or overflow_count % 50 == 0:
                dut._log.info(f"[Ciclo {i:3d}] Overflow #{overflow_count}: mag={magnitude:5d}")
    
    # -----------------------------------------------------------
    # 5. Reporte Final de Resultados
    # -----------------------------------------------------------
    dut._log.info("")
    dut._log.info("="*60)
    dut._log.info("RESULTADOS DE VERIFICACIÓN ESTÁNDAR (RANDOM)")
    dut._log.info("="*60)
    dut._log.info(f"Total de Ciclos:              {ITERATIONS}")
    dut._log.info(f"Total de Overflows:           {overflow_count}")
    dut._log.info(f"Tasa de Overflow:             {100*overflow_count/ITERATIONS:.2f}%")
    dut._log.info(f"Magnitud Máxima Alcanzada:    {max_magnitude_reached}")
    
    if first_overflow_cycle is not None:
        dut._log.info(f"Primer Overflow en Ciclo:     {first_overflow_cycle}")
    else:
        dut._log.info(f"Primer Overflow en Ciclo:     NINGUNO")
    
    dut._log.info(f"Coeficientes usados:          {current_coeffs}")
    dut._log.info("="*60)
    
    # -----------------------------------------------------------
    # 6. Visualización de Resultados
    # -----------------------------------------------------------
    try:
        plt.figure(figsize=(12, 6))
        
        # Plot de magnitudes
        plt.plot(history_magnitudes, linewidth=1, alpha=0.7, label='Magnitud')
        
        # Línea de umbral de overflow
        plt.axhline(y=16000, color='r', linestyle='--', linewidth=2, 
                   label='Umbral de Overflow (16000)')
        
        # Media móvil para ver tendencia (ventana de 20)
        if len(history_magnitudes) >= 20:
            window = 20
            moving_avg = []
            for idx in range(len(history_magnitudes)):
                if idx < window:
                    moving_avg.append(sum(history_magnitudes[:idx+1])/(idx+1))
                else:
                    moving_avg.append(sum(history_magnitudes[idx-window+1:idx+1])/window)
            plt.plot(moving_avg, color='orange', linewidth=2, 
                    label=f'Media Móvil ({window} ciclos)')
        
        plt.title(f'Verificación ESTÁNDAR (Random) - Coefs: {current_coeffs}')
        plt.xlabel('Ciclo de Simulación')
        plt.ylabel('Magnitud de Salida')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # Guardar gráfico
        output_filename = "random_verification_curve.png"
        plt.savefig(output_filename, dpi=150)
        dut._log.info(f"Gráfico guardado como: {output_filename}")
        
    except Exception as e:
        dut._log.warning(f"No se pudo generar gráfico: {e}")
    
    dut._log.info("")
    dut._log.info("Simulación COMPLETADA")
