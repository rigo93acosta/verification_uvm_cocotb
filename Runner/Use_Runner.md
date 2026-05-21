# Guia de uso del runner Cocotb

Este documento explica paso a paso el flujo del archivo `runner_tb_mux.py` y como usarlo para correr simulaciones con Cocotb. Tambien incluye un ejemplo teorico con varios ficheros RTL y Python.

## Objetivo

- Ejecutar pruebas Cocotb sobre un diseno RTL.
- Elegir el simulador mediante la variable de entorno `SIM`.
- Generar trazas (waves) de manera consistente.
- Convertir WLF a VCD/FST cuando se usa Questa.

## Requisitos previos

- Python instalado.
- Cocotb instalado (incluye `cocotb_tools.runner`).
- Simulador disponible: Verilator, Icarus o Questa/ModelSim.
- Archivos RTL y testbench Cocotb en el mismo proyecto.

## Estructura minima esperada

- `mux.sv`: modulo RTL toplevel.
- `mux_tb.py`: test Cocotb.
- `runner_tb_mux.py`: runner que compila y ejecuta.

## Paso a paso del runner

1) Leer el simulador desde entorno
- Se lee `SIM` y se normaliza a minusculas.
- Si no se define, usa `verilator` por defecto.

2) Mapeo de nombres de simulador
- Se aceptan alias comunes: `iverilog` -> `icarus`, `modelsim` -> `questa`.
- Si el valor no esta soportado, se lanza `ValueError`.

3) Definir rutas del proyecto
- Se obtiene el directorio del archivo con `Path(__file__).resolve().parent`.
- Se definen las fuentes RTL con `sources = [proj_path / "mux.sv"]`.

4) Crear el runner
- Se instancia con `get_runner(sim)`.
- Esto selecciona el backend correcto segun el simulador.

5) Definir argumentos de build
- Para Verilator se habilitan trazas con `--trace` y `--trace-fst`.
- Para otros simuladores se deja vacio.

6) Compilar (build)
- Se llama `runner.build(...)` con:
  - `sources`: lista de RTL.
  - `hdl_toplevel`: nombre del modulo toplevel.
  - `always=True`: recompila siempre.
  - `timescale`: `1ns/1ns`.
  - `build_args`: opciones por simulador.
  - `waves=True`: activa dumps de ondas.

7) Ejecutar test
- Se llama `runner.test(...)` con:
  - `hdl_toplevel`: toplevel.
  - `test_module`: modulo Python (sin .py).
  - `waves=True`: mantener trazas.

8) Post-proceso para Questa
- Se busca `sim_build/vsim.wlf`.
- Si existe, se intenta convertir a VCD con `wlf2vcd`.
- Si hay VCD y existe `vcd2fst`, se convierte a FST.
- Errores de conversion se ignoran para no fallar el test.

## Como usar el runner

### Ejecucion basica

- Verilator (por defecto):

```bash
python runner_tb_mux.py
```

- Icarus:

```bash
SIM=icarus python runner_tb_mux.py
```

- Questa/ModelSim:

```bash
SIM=questa python runner_tb_mux.py
```

### Ejecucion con uv y pytest

- Ejemplo con Questa:

```bash
SIM=questa uv run pytest runner_tb_mux.py -s
```

### Resultado esperado

- Carpeta `sim_build/` con binarios de simulacion.
- Dumps de ondas (FST/VCD) si el simulador lo permite.
- Salida de Cocotb con el estado de los tests.

## Ejemplo teorico con varios ficheros

### Estructura

```
my_project/
  rtl/
    alu.sv
    adder.sv
    mux2.sv
  tb/
    test_alu.py
    test_adder.py
  runner.py
```

### RTL (ejemplo simplificado)

`rtl/adder.sv`
```systemverilog
module adder #(parameter W=8) (
  input  logic [W-1:0] a,
  input  logic [W-1:0] b,
  output logic [W-1:0] y
);
  assign y = a + b;
endmodule
```

`rtl/mux2.sv`
```systemverilog
module mux2 #(parameter W=8) (
  input  logic [W-1:0] d0,
  input  logic [W-1:0] d1,
  input  logic         sel,
  output logic [W-1:0] y
);
  assign y = sel ? d1 : d0;
endmodule
```

`rtl/alu.sv`
```systemverilog
module alu #(parameter W=8) (
  input  logic [W-1:0] a,
  input  logic [W-1:0] b,
  input  logic         sel,
  output logic [W-1:0] y
);
  logic [W-1:0] add_y;
  adder #(W) u_add (.a(a), .b(b), .y(add_y));
  mux2  #(W) u_mux (.d0(a), .d1(add_y), .sel(sel), .y(y));
endmodule
```

### Cocotb (dos tests)

`tb/test_adder.py`
```python
import cocotb
from cocotb.triggers import Timer

@cocotb.test()
async def test_adder_basic(dut):
    dut.a.value = 3
    dut.b.value = 5
    await Timer(1, units="ns")
    assert int(dut.y.value) == 8
```

`tb/test_alu.py`
```python
import cocotb
from cocotb.triggers import Timer

@cocotb.test()
async def test_alu_add_select(dut):
    dut.a.value = 2
    dut.b.value = 4
    dut.sel.value = 1
    await Timer(1, units="ns")
    assert int(dut.y.value) == 6
```

### Runner (runner.py)

```python
import os
from pathlib import Path
from cocotb_tools.runner import get_runner


def main():
    sim = os.getenv("SIM", "verilator").lower()
    sim_map = {
        "verilator": "verilator",
        "iverilog": "icarus",
        "icarus": "icarus",
        "questa": "questa",
        "modelsim": "questa",
    }
    if sim not in sim_map:
        raise ValueError(f"SIM no soportado: {sim}")

    proj = Path(__file__).resolve().parent
    sources = [
        proj / "rtl" / "adder.sv",
        proj / "rtl" / "mux2.sv",
        proj / "rtl" / "alu.sv",
    ]

    runner = get_runner(sim_map[sim])
    build_args = ["--trace", "--trace-fst", "--trace-structs"] if sim_map[sim] == "verilator" else []

    runner.build(
        sources=sources,
        hdl_toplevel="alu",
        timescale=["1ns", "1ns"],
        build_args=build_args,
        waves=True,
        always=True,
    )

    runner.test(
        hdl_toplevel="alu",
        test_module="test_alu",
        waves=True,
    )


if __name__ == "__main__":
    main()
```

## Consejos practicos

- Asegura que `hdl_toplevel` coincide con el nombre del modulo en RTL.
- `test_module` debe ser el nombre del archivo Python sin extension.
- Para multiples tests, correlos en ejecuciones separadas o usa un runner que itere modulos.
- Si el simulador no genera ondas, desactiva `waves`.


## Skills de AI

En la carpeta runner-cocotb se ha generado una skill con template para crear runners personalizados. Esto permite a los usuarios generar scripts de runner adaptados a sus necesidades especificas, como agregar opciones de simulacion, configurar entornos de prueba, o integrar con sistemas de CI/CD. La skill puede ser utilizada para acelerar el desarrollo de runners y asegurar consistencia en la ejecucion de pruebas Cocotb.

