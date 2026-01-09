# Testbench de Multiplicador con Cocotb

## Descripción General

Este proyecto implementa un testbench de verificación para un multiplicador digital utilizando Cocotb, una biblioteca de Python para simulación de HDL. El testbench sigue un patrón similar al UVM (Universal Verification Methodology), estructurado en componentes modulares para generar estímulos aleatorios, inyectarlos al DUT, monitorear respuestas y comparar resultados esperados.

## Archivos en la Carpeta

- **mult_tb.py**: Archivo principal del testbench en Python. Contiene las clases del testbench y la función de prueba principal.
- **makefile**: Archivo de construcción para compilar y ejecutar la simulación usando Icarus Verilog y Cocotb.
- **mult.sv**: Módulo Verilog del Device Under Test (DUT), un multiplicador combinacional de 4x4 bits.
- **mult.vcd**: Archivo de ondas generado por la simulación (creado después de ejecutar).

## Descripción del DUT

El DUT es un módulo Verilog llamado `mult` que realiza una multiplicación combinacional entre dos números de 4 bits (`a` y `b`), produciendo un resultado de 8 bits (`y`). La operación es `y = a * b`. Es un circuito puramente combinacional, sin lógica secuencial, y se simula usando Icarus Verilog.

### Entity: mult 
- **File**: mult.sv

### Diagram
![Diagram](mult.svg "Diagram")
### Ports

| Port name | Direction | Type  | Description |
| --------- | --------- | ----- | ----------- |
| a         | input     | [3:0] |             |
| b         | input     | [3:0] |             |
| y         | output    | [7:0] |             |


## Proceso de Verificación (Patrón UVM-like)

El testbench sigue un flujo de verificación estructurado similar a UVM, dividido en las siguientes fases/componentes:

1. **Transaction**: Clase que representa los datos de entrada/salida (a, b, y). Incluye randomización para generar estímulos aleatorios.

2. **Generator**: Genera transacciones aleatorias y las envía a una cola. Espera eventos para sincronizar con el scoreboard.

3. **Driver**: Recibe transacciones de la cola y las aplica a las entradas del DUT. Espera un tiempo fijo para permitir la estabilización.

4. **Monitor**: Muestrea las salidas del DUT y las entradas actuales, creando transacciones de respuesta que envía al scoreboard.

5. **Scoreboard**: Compara los resultados muestreados con los valores esperados (a * b). Registra PASS/FAIL y notifica al generator para continuar.

El flujo es asíncrono y concurrente, con tareas corriendo en paralelo usando `cocotb.start_soon`.

## Detalles de Timing

El timing en la simulación está controlado por timers de Cocotb para asegurar la sincronización correcta:

- **Driver**: Después de aplicar entradas (a, b), espera `Timer(10, unit="ns")` para permitir que la lógica combinacional se estabilice.
- **Monitor**: Espera `Timer(5, unit="ns")` al inicio de cada ciclo de muestreo para evitar muestrear valores no inicializados ('x'). Luego, después de muestrear, espera otro `Timer(5, unit="ns")` antes de enviar la transacción (total 10ns por ciclo).
- **Test Principal**: Corre por `Timer(60, unit="ns")`, suficiente para 10 pruebas (aprox. 6ns por prueba en promedio).

Esto asegura que el monitor no intente convertir valores no resueltos a enteros, evitando errores de "LogicArray contains non-0/1 values".

## Cómo Ejecutar

1. Asegúrate de tener el entorno virtual activado: `source .venv/bin/activate` (usando uv).
2. En el directorio del proyecto: `cd Proyect/p1_mult`
3. Ejecuta: `make`
4. Revisa los logs en la consola y el archivo `*.vcd` para ver los resultados en gtkwave.

## Dependencias

- Python >= 3.12
- Cocotb >= 2.0.1
- Cocotb-bus >= 0.3.0
- Cocotb-coverage >= 2.0
- Icarus Verilog (para simulación HDL)
- Gtkwave (para visualizar archivos VCD)

Este setup permite una verificación automatizada y reproducible del multiplicador.