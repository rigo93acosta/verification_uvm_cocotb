#!/usr/bin/env python3
import sys
import os

if len(sys.argv) != 5:
    print("Uso: python create_makefile.py <archivo_sv> <top_module> <testbench> <ruta_carpeta>")
    print("Ejemplo: python create_makefile.py mult.sv mult mult_tb /path/to/folder")
    sys.exit(1)

sv_file = sys.argv[1]
top_module = sys.argv[2]
testbench = sys.argv[3]
folder_path = sys.argv[4]

# Crear la carpeta si no existe
os.makedirs(folder_path, exist_ok=True)

# Contenido del makefile basado en la referencia
makefile_content = f"""TOPLEVEL_LANG ?= verilog
SIM ?= icarus
VERILOG_SOURCES = $(shell pwd)/{sv_file}
TOPLEVEL := {top_module} # Verilog or SystemVerilog TOP file module name
COCOTB_TEST_MODULES   := {testbench} # Python file name

include $(shell cocotb-config --makefiles)/Makefile.sim
"""

# Ruta completa del makefile
makefile_path = os.path.join(folder_path, 'makefile')

# Escribir el makefile
with open(makefile_path, 'w') as f:
    f.write(makefile_content)

# Crear el archivo SV básico
sv_content = f"""module {top_module} (
    // Definir entradas y salidas aquí
    input wire clk,
    input wire rst,
    // Agregar más puertos según sea necesario
    output reg [7:0] out
);

// Lógica del módulo aquí
// Ejemplo básico
always @(posedge clk or posedge rst) begin
    if (rst) begin
        out <= 8'b0;
    end else begin
        // Lógica personalizada
        out <= out + 1;
    end
end

endmodule
"""

sv_path = os.path.join(folder_path, sv_file)
with open(sv_path, 'w') as f:
    f.write(sv_content)

# Crear el archivo Python testbench básico
py_content = f"""import cocotb
from cocotb.triggers import Timer

@cocotb.test()
async def test_{top_module}(dut):
    \"\"\"Test básico para {top_module}\"\"\"
    # Inicializar señales
    dut.rst.value = 1
    dut.d.value = 0
    await Timer(10, units='ns')
    dut.rst.value = 0
    
    # Simular algunos ciclos de reloj con diferentes valores de d
    test_values = [0, 1, 0, 1, 1, 0, 0, 1]
    for i, d_val in enumerate(test_values):
        dut.d.value = d_val
        dut.clk.value = 0
        await Timer(5, units='ns')
        dut.clk.value = 1
        await Timer(5, units='ns')
        # Verificar que q sigue a d después del flanco de reloj
        print(f"Ciclo {{i}}: d = {{int(dut.d.value)}}, q = {{int(dut.q.value)}}")
        if i > 0:  # Después del primer ciclo, q debería ser el d anterior
            expected_q = test_values[i-1]
            assert int(dut.q.value) == expected_q, f"Esperado q={{expected_q}}, obtenido {{int(dut.q.value)}}"
"""

py_file = f"{testbench}.py"
py_path = os.path.join(folder_path, py_file)
with open(py_path, 'w') as f:
    f.write(py_content)

print(f"Makefile creado en: {makefile_path}")
print(f"Archivo SV creado en: {sv_path}")
print(f"Archivo Python testbench creado en: {py_path}")