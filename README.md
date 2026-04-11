# Python Verification with UVM and cocotb

Este proyecto es una colección de ejercicios y proyectos para aprender verificación utilizando Universal Verification Methodology (UVM) con cocotb para diseños en Verilog. Está diseñado para estudiantes o desarrolladores interesados en la verificación de hardware digital.

## Dependencias

El proyecto requiere las siguientes bibliotecas de Python:
- cocotb (>=2.0.1): Para la simulación y verificación de diseños Verilog desde Python.
- pandas (>=2.3.3): Para el manejo de datos.
- pytest (>=9.0.2): Para pruebas unitarias.
- pyuvm (>=4.0.1): Para implementar UVM en Python.

Puedes instalar las dependencias usando `pip` o `uv` (como se ve en el archivo `pyproject.toml`).

## Herramientas del Sistema

Además de las bibliotecas de Python, el proyecto requiere las siguientes herramientas del sistema para la simulación de Verilog y visualización de waveforms:
- **Icarus Verilog** (iverilog): Simulador de Verilog utilizado en los makefiles para compilar y ejecutar las simulaciones.
- **GTKWave**: Visor de waveforms para analizar los archivos `.vcd` generados durante las simulaciones.
- **Surfer** (opcional): Visor moderno de waveforms (por ejemplo `.vcd`/`.fst`). Proyecto original: https://github.com/surfer-project/surfer

Asegúrate de instalar estas herramientas en tu sistema. En Ubuntu/Debian, puedes usar:
```bash
sudo apt-get install iverilog gtkwave
```

> Nota: Surfer es opcional y no siempre está disponible vía `apt`. Para instalarlo, consulta las instrucciones oficiales del proyecto: https://github.com/surfer-project/surfer

En otras distribuciones de Linux, consulta la documentación oficial de cada herramienta.

## Estructura del Proyecto

### main.py
Este es el script principal que verifica la instalación de las bibliotecas esenciales necesarias para el proyecto. Al ejecutarlo, imprime un mensaje de bienvenida y comprueba si todas las dependencias están disponibles. Si alguna falta, te informa para que la instales.

### Course_1
Esta carpeta contiene módulos de Python básicos que sirven como utilidades para operaciones relacionadas con la verificación y el manejo de datos binarios. Incluye:
- `v_binaries.py`: Demuestra operaciones binarias básicas (AND, OR, XOR, NOT).
- `v_binary_types.py`: Utilidades para tipos de datos binarios.
- `v_decorator.py`: Decoradores para funciones.
- `v_loggin.py`: Utilidades para logging (probablemente un módulo de logging personalizado).
- `v_random.py`: Funciones para generación de números aleatorios.
- `v_random_choice.py`: Selección aleatoria de elementos.

Estos módulos proporcionan herramientas fundamentales para el curso de verificación.

### Course_2
Esta carpeta contiene proyectos prácticos de verificación de diseños Verilog utilizando cocotb. Cada subcarpeta representa un proyecto específico con su módulo Verilog, testbench en Python, y archivos de simulación. Incluye:
- `4bit_adder/`: Verificación de un sumador de 4 bits.
- `8_1_mux/`: Verificación de un multiplexor 8:1.
- `binary/`: Proyecto relacionado con operaciones binarias.
- `clock/`: Verificación de señales de reloj.
- `d_flip_flop/`: Verificación de un flip-flop D.
- `functions/`: Verificación de funciones en Verilog.
- `memory/`: Verificación de memoria.
- `pri_encoder/`: Verificación de un codificador de prioridad.
- `Project_1/`: Proyecto 1, que incluye sumadores.
- `rac_4bit/`: Sumador carry ripple de 4 bits.
- `reset/`: Verificación con señales de reset.
- `start_soon/`: Proyecto de inicio rápido.

Cada proyecto incluye:
- Archivos `.sv`: Módulos Verilog.
- Archivos `_tb.py`: Testbenches escritos con cocotb.
- `makefile`: Para compilar y ejecutar simulaciones.
- `results.xml`: Resultados de las pruebas.
- `dump.vcd` (o `.fst`, según simulador): Archivos de waveform para análisis (visibles en GTKWave o Surfer).
- `sim_build/`: Archivos generados durante la simulación.

### Course_3
Esta carpeta contiene proyectos avanzados de verificación de diseños Verilog utilizando cocotb, enfocándose en conceptos como clases, transacciones, IPC y entornos de verificación. Cada subcarpeta representa un proyecto específico con su módulo Verilog, testbench en Python, y archivos de simulación. Incluye:
- `classes_trans/`: Verificación utilizando clases y transacciones.
- `classIPC/`: Comunicación entre procesos con clases.
- `env_verification/`: Entornos de verificación completos.
- `ipc/`: Comunicación entre procesos.
- `prj_1_all/`: Proyecto integral combinando múltiples conceptos.
- `random/`: Verificación con generación aleatoria.
- `transaction/`: Manejo de transacciones en verificación.

Cada proyecto incluye:
- Archivos `.sv`: Módulos Verilog.
- Archivos `_tb.py`: Testbenches escritos con cocotb.
- `makefile`: Para compilar y ejecutar simulaciones.
- `results.xml`: Resultados de las pruebas.
- `dump.vcd` (o `.fst`, según simulador): Archivos de waveform para análisis (visibles en GTKWave o Surfer).
- `sim_build/`: Archivos generados durante la simulación.

### Course_4
Esta carpeta contiene proyectos especializados de verificación avanzada utilizando patrones UVM-like con cocotb. Cada proyecto incluye una documentación detallada en un archivo Markdown dedicado.

- **1_Combinational/**: Verificación de un multiplicador combinacional 4x4 con testbench estructurado (generator/driver/monitor/scoreboard). [Ver detalles](Course_4/1_Combinational/Test_Multiplicador.md)
- **2_DFF/**: Verificación de un D flip-flop con testbench estructurado. [Ver detalles](Course_4/2_DFF/Test_DFF.md)
- **3_FIFO/**: Verificación de un FIFO síncrono con testbench estructurado. [Ver detalles](Course_4/3_FIFO/Test_FIFO.md)
- **4_SPI/**: Verificación de un sistema SPI (Master + integración Master/Slave). [Ver detalles](Course_4/4_SPI/Test_SPI_Master.md)
- **5_I2C/**: Verificación de un sistema I2C completo (open-drain + pull-ups). [Ver detalles](Course_4/5_I2C/Test_I2C.md)
- **6_UART/**: Verificación de un sistema UART completo. [Ver detalles](Course_4/6_UART/Test_UART.md)

#### Nuevo formato de `makefile` (selección por TEST) — ejemplo en `Course_4/4_SPI/`

En algunos proyectos (por ejemplo, `Course_4/4_SPI/`) el `makefile` está diseñado para ejecutar **más de un test cocotb** con el mismo set de fuentes Verilog/SystemVerilog, seleccionando automáticamente el `TOPLEVEL` y los archivos a compilar según el test que quieras correr.

- **Selección de test**: usa `TEST=<modulo_tb>` (sin `.py`).
	- `make TEST=spi_master_tb` corre el test del master (TOPLEVEL `SPI_MASTER`).
	- `make TEST=master_slave_tb` corre el test de integración master+slave (TOPLEVEL `master_slave`).
- **Targets útiles**:
	- `make help` muestra opciones.
	- `make test_all` ejecuta ambos tests.
- **Overrides típicos**:
	- `make SIM=icarus ...` cambia el simulador (por defecto `icarus`).
	- `make WAVES=1 ...` habilita dumps de waveforms (si el simulador lo soporta).

Este patrón evita duplicar `makefile`s por test y mantiene centralizada la selección de `TOPLEVEL`/`VERILOG_SOURCES`. Para analizar waveforms, puedes usar GTKWave o Surfer.

## Cómo Usar

1. Asegúrate de tener Python >=3.12 instalado.
2. Instala las dependencias: `uv sync` o `pip install -e .`
3. Ejecuta `uv run main.py` para verificar las bibliotecas.
4. Navega a cualquier proyecto en `Course_2`, `Course_3` o `Course_4` y ejecuta `make` para simular.

Este proyecto es ideal para aprender verificación de hardware paso a paso, desde conceptos básicos en Python hasta implementaciones completas en Verilog con UVM.

---

## Proyecto Especial: Verificación Guiada por Machine Learning (ML_cocotb/)

### Introducción

Este proyecto innovador implementa **verificación funcional dirigida por aprendizaje automático (Machine Learning-Guided Verification)** para un filtro digital FIR (Finite Impulse Response) de segundo orden. La metodología combina técnicas de verificación tradicionales basadas en cocotb con algoritmos de ML para optimizar la generación de estímulos de prueba, logrando una convergencia 100-1000x más rápida que métodos aleatorios.

### Arquitectura del Sistema

#### Diseño Bajo Test (DUT): `filter.v`
```
Entradas: clk, rst, data_in[7:0], coeff0, coeff1, coeff2 [7:0]
Salidas: data_out[15:0], overflow_detected
Implementación: y[n] = x[n]·c0 + x[n-1]·c1 + x[n-2]·c2
```

#### Agentes de Machine Learning
Se implementan tres enfoques de complejidad creciente:

1. **Agente Clasificador** (`ml_agent.py`): Clasificación binaria para predecir overflow
2. **Agente Regresor** (`ml_agent_regressor.py`): Regresión para predecir magnitud de salida
3. **Agente Temporal** (`ml_temporal_agent.py`): Regresión con memoria temporal (Sliding Window)

#### Testbenches
- `test_fir_ml.py`: Testbench con clasificador (200 iteraciones)
- `test_fir_ml_regressor.py`: Testbench con regresor (300 iteraciones)
- `test_fir_ml_memory.py`: Testbench temporal avanzado (600 iteraciones)

### Resultados Clave

| Agente | Iteraciones para 1er overflow | Características |
|--------|-------------------------------|-----------------|
| **Clasificador** | ~50-150 | Funciona, pero warnings de sklearn |
| **Regresor** | ~5-20 | Mejor, converge rápido |
| **Temporal** | ~3-10 | Óptimo, aprende secuencias |

### Innovaciones Técnicas

1. **Sliding Window para Contexto Temporal**: Primera implementación de memoria temporal en verificación de filtros FIR
2. **Epsilon-Greedy Strategy**: Balancea exploración y explotación
3. **Visualizaciones Avanzadas**: Gráficos con media móvil y umbrales de overflow
4. **Comparación Empírica**: Tres paradigmas ML evaluados sistemáticamente

### Impacto Potencial

- **Reducción de tiempo de verificación**: 10-100x en casos complejos
- **Mejora de cobertura**: Descubrimiento automático de corner cases
- **Democratización**: No requiere experiencia profunda en verificación formal

### Cómo Ejecutar

```bash
cd ML_cocotb/
# Ejecutar con agente temporal (recomendado)
make SIM=icarus TOPLEVEL=filter MODULE=test_fir_ml_memory
```

### Documentación Detallada

Para información completa, incluyendo fundamentos matemáticos, teoría de ML aplicada, limitaciones y trabajo futuro, consulte el [README.md detallado](ML_cocotb/README.md) en la carpeta `ML_cocotb/`.

Este proyecto representa el estado del arte en verificación automatizada y sirve como puente entre la verificación tradicional y las técnicas emergentes de IA aplicadas a la ingeniería de hardware.