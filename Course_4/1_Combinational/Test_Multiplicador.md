# Testbench de Multiplicador con Cocotb

## Descripción General

Este proyecto implementa un testbench de verificación para un multiplicador digital utilizando Cocotb, una biblioteca de Python para simulación de HDL. El testbench sigue un patrón similar al UVM (Universal Verification Methodology), estructurado en componentes modulares para generar estímulos aleatorios, inyectarlos al DUT, monitorear respuestas y comparar resultados esperados.

## Archivos en la Carpeta

- **mult_tb.py**: Testbench principal en Python (Cocotb). Contiene las clases `Transaction`, `Generator`, `Driver`, `Monitor` y `Scoreboard`, y la prueba parametrizada `mult_test`.
- **runner_mult.py**: Script de ayuda que usa `cocotb_tools.runner` para compilar y ejecutar la simulación con distintos backends (verilator, icarus/iverilog, questa/modelsim).
- **mult.sv**: Módulo Verilog del Device Under Test (DUT), un multiplicador combinacional de 4x4 bits.
- **mult.svg**: Diagrama/imagen del DUT usado en la documentación.
- **sim_build/**: Carpeta de salida de la build/simulación (creada por el runner/HDL simulator).
- **__pycache__/**: Caché de Python generado al ejecutar los scripts.

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

## Detalles de Timing y flujo

El testbench usa parámetros para controlar el número de pruebas y los delays; no hay un tiempo fijo único. Puntos clave:

- **Driver**: aplica `a` y `b` al DUT y espera `Timer(delay, unit="ns")` (el `delay` se pasa como parámetro a la tarea `drive_data`).
- **Monitor**: muestrea la señal intermedia esperando `delay//2` antes y `delay//2` después para evitar leer valores no inicializados y dar tiempo a estabilización de señales.
- **Generator / Test**: la prueba `mult_test` está parametrizada con `num_tests` y `delay` (ej.: 10, 50, 100 tests; delays 6, 10, 20 ns). El generador termina al completar `NUM_TESTS` transacciones; el test espera hasta que las colas estén vacías.

Esta estructura evita errores por valores 'x' al convertir `LogicArray` a enteros y permite flexibilidad para diferentes simuladores y velocidades.

## Cómo Ejecutar

Este repositorio incluye `runner_mult.py` como helper para construir y ejecutar las pruebas con distintos motores de simulación.

Ejemplos:

- Ejecutar con el simulador por defecto (por defecto `verilator`):

```bash
python3 runner_mult.py
```

- Elegir simulador (por ejemplo `icarus`/`iverilog` o `questa`):

```bash
SIM=icarus python3 runner_mult.py
SIM=questa python3 runner_mult.py
```

El script usa `cocotb_tools.runner` internamente y generará la carpeta `sim_build/` con los artefactos. Para visualizar ondas, abre el fichero de trazas generado por tu simulador (`.vcd`, `.fst` o `.wlf`) con GTKWave o la herramienta que prefieras.

- Ejecutar los tests usando `pytest` mediante `uv` y seleccionando Questa:

```bash
SIM=questa uv run pytest -s -q runner_mult.py
```

## Dependencias

- Python 3.8+ (o la versión que uses en el entorno de desarrollo).
- cocotb (version compatible con tu entorno; cualquier 1.x/2.x reciente debería funcionar).
- cocotb-coverage (opcional, usado en el test para randomización y cobertura).
- cocotb_tools (para `runner_mult.py`).
- Un backend de simulación: `verilator`, `iverilog`/`icarus`, o `questa`/`modelsim` según prefieras.
- GTKWave (u otra herramienta) para visualizar `.vcd`/`.fst`.

Instalación rápida (ejemplo con pip):

```bash
python -m pip install -r requirements.txt
```

Si no tienes `requirements.txt`, instala mínimo:

```bash
python -m pip install cocotb cocotb-tools cocotb-coverage
```

Con esto puedes ejecutar `python3 runner_mult.py` y cambiar el backend con la variable de entorno `SIM`.

Este README está actualizado para reflejar los archivos reales y el uso del `runner_mult.py` en esta carpeta.

Nota sobre `uv`:

- Puedes emplear `uv` para crear/gestionar el entorno virtual y ejecutar comandos dentro de él. Por ejemplo, usar `uv run` permite ejecutar `pytest` o `python` dentro del entorno aislado.