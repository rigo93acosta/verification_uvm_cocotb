**Verificación Pos-síntesis con Yosys**

Breve: descripción del flujo usado para verificar el comportamiento funcional de un diseño después de sintetizarlo con Yosys.

- **Objetivo**: Verificar que el netlist generado por Yosys (`dff_synth.v`) mantiene la funcionalidad del RTL original `dff.sv` cuando se ejecuta con el testbench Cocotb.

**Archivos clave**
- **synth.ys**: Script de Yosys que lee el SystemVerilog y genera el netlist sintetizado. Ver [PosSynVerification/synth.ys](PosSynVerification/synth.ys#L1-L7).
- **dff.sv**: Código RTL original (flop D) usado como entrada para síntesis. Ver [PosSynVerification/dff.sv](PosSynVerification/dff.sv#L1-L20).
- **dff_synth.v**: Netlist Verilog generado por Yosys (resultado de la síntesis). Ver [PosSynVerification/dff_synth.v](PosSynVerification/dff_synth.v#L1-L40).
- **dff_tb.py**: Testbench en Cocotb que genera vectores, ejerce el DUT y comprueba resultados mediante un `Scoreboard`. Ver [PosSynVerification/dff_tb.py](PosSynVerification/dff_tb.py#L1-L200).
- **run_synth_test.py**: Script auxiliar que prepara la simulación del netlist sintetizado, añade `simlib.v` de Yosys y ejecuta el test usando el runner de `cocotb_tools`. Ver [PosSynVerification/run_synth_test.py](PosSynVerification/run_synth_test.py#L1-L200).

**Requisitos previos**
- Yosys instalado y accesible en `PATH` (o `yosys-config` disponible) para localizar `datdir` y `simlib.v`.
- Un simulador soportado por `cocotb_tools` (por ejemplo Icarus/iverilog, Verilator o Questa/Modelsim).
- Python con `cocotb`, `cocotb_tools` y dependencias instaladas en el entorno.

**Flujo paso a paso**

1. Generar el netlist sintetizado con Yosys

   - Sitúate en el directorio `PosSynVerification` y ejecuta Yosys con el script:

   ```bash
   cd PosSynVerification
   yosys synth.ys
   ```

   - Resultado: se crea `dff_synth.v` (ya incluido en este repositorio como ejemplo). El script `synth.ys` realiza:
     - `read_verilog -sv dff.sv`
     - `hierarchy -check -top dff`
     - `synth -top dff`
     - `write_verilog dff_synth.v`

2. Preparar la simulación pos-síntesis

   - El testbench en `dff_tb.py` está escrito en Cocotb y contiene:
     - Generador de transacciones aleatorias (`Generator` / `Transaction`).
     - `Driver` que aplica señales de entrada y resetea el DUT.
     - `Monitor` y `Scoreboard` que comparan `dout` vs `din`.
   - El script `run_synth_test.py` automatiza la preparación y ejecución de la simulación para el netlist sintetizado. Puntos importantes:
     - Detecta `datdir` de Yosys (usando `yosys-config` o `yosys --datdir`) para localizar `simlib.v`.
     - Añade `simlib.v` a la lista de fuentes, necesaria para simular instancias lógicas generadas por Yosys.
     - Llama al runner de `cocotb_tools` para compilar y ejecutar la simulación en `sim_build_synth`.

3. Ejecutar la simulación pos-síntesis

   - Ejemplo de ejecución (simulador por defecto `icarus`):

   ```bash
   cd PosSynVerification
   python3 run_synth_test.py
   ```

   - Para seleccionar un simulador diferente, exporta `SIM` antes de ejecutar. Ejemplos:

   ```bash
   SIM=verilator python3 run_synth_test.py
   SIM=questa python3 run_synth_test.py
   SIM=icarus python3 run_synth_test.py
   ```

   - Salidas esperadas:
     - Directorio `sim_build_synth` con compilación y ficheros intermedios.
     - Mensajes de log desde Cocotb indicando pasos de `Generator`, `Driver`, `Monitor` y `Scoreboard`.
     - En consola aparecerá `Test Passed` o `Test Failed` dependiendo de la comparación del `Scoreboard`.
     - Para Verilator se pueden generar trazas (`.fst`, `.vcd`) si están habilitadas.

**Notas importantes y depuración**
- Si `run_synth_test.py` falla con error sobre `simlib.v`, asegúrate de que Yosys está instalado y que `yosys-config --datdir` devuelve un directorio válido (normalmente `/usr/share/yosys`).
- `simlib.v` contiene implementaciones de celdas lógicas usadas por Yosys; es obligatorio para simular el netlist generado.
- Si hay diferencias funcionales entre RTL y netlist revisa:
  - Síncronización de `rst` y `clk` en el testbench.
  - Adecuación de la semántica de señales (por ejemplo, si Yosys llevó a implementación con flops asíncronos u optimizaciones no previstas).

**Resultado de ejemplo incluido**
- En este repositorio ya está presente `dff_synth.v` (netlist generado). Puedes examinarlo en: [PosSynVerification/dff_synth.v](PosSynVerification/dff_synth.v#L1-L40).

**Conclusión**
- El flujo pos-síntesis realizado consiste en sintetizar con Yosys, añadir `simlib.v` y ejecutar el testbench Cocotb sobre el netlist resultante. Esto permite verificar que la síntesis no ha modificado el comportamiento funcional del módulo `dff`.

**Referencias (archivos)**
- [PosSynVerification/synth.ys](PosSynVerification/synth.ys#L1-L7)
- [PosSynVerification/dff.sv](PosSynVerification/dff.sv#L1-L20)
- [PosSynVerification/dff_synth.v](PosSynVerification/dff_synth.v#L1-L40)
- [PosSynVerification/dff_tb.py](PosSynVerification/dff_tb.py#L1-L200)
- [PosSynVerification/run_synth_test.py](PosSynVerification/run_synth_test.py#L1-L200)

