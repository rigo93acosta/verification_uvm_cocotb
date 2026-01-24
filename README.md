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

Asegúrate de instalar estas herramientas en tu sistema. En Ubuntu/Debian, puedes usar:
```bash
sudo apt-get install iverilog gtkwave
```

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
- `dump.vcd`: Archivos de waveform para análisis.
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
- `dump.vcd`: Archivos de waveform para análisis.
- `sim_build/`: Archivos generados durante la simulación.

### Course_4
Esta carpeta contiene proyectos especializados de verificación avanzada utilizando patrones UVM-like con cocotb. Cada proyecto incluye una documentación detallada en un archivo Markdown dedicado.

- **p1_mult/**: Verificación de un multiplicador combinacional de 4x4 bits utilizando un testbench estructurado con generador, driver, monitor y scoreboard. [Ver detalles](Course_4/p1_mult/Testbench%20de%20Multiplicador.md)
- **d_flip_flop/**: Verificación de un D flip-flop síncrono con reset asíncrono utilizando un testbench estructurado con generador, driver, monitor y scoreboard. [Ver detalles](Course_4/d_flip_flop/Testbench%20de%20D%20Flip-Flop.md)
- **fifo/**: Verificación de un FIFO síncrono utilizando un testbench estructurado con generador, driver, monitor y scoreboard. [Ver detalles](Course_4/fifo/Testbench%20de%20FIFO.md)

## Cómo Usar

1. Asegúrate de tener Python >=3.12 instalado.
2. Instala las dependencias: `uv sync` o `pip install -e .`
3. Ejecuta `uv run main.py` para verificar las bibliotecas.
4. Navega a cualquier proyecto en `Course_2`, `Course_3` o `Course_4` y ejecuta `make` para simular.

Este proyecto es ideal para aprender verificación de hardware paso a paso, desde conceptos básicos en Python hasta implementaciones completas en Verilog con UVM.