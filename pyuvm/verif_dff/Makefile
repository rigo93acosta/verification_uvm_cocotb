# Makefile para cocotb/pyuvm

# Simulador a usar (icarus verilog es gratuito)
SIM ?= icarus
TOPLEVEL_LANG ?= verilog

# Archivos de fuentes Verilog (.v)
VERILOG_SOURCES += $(PWD)/dff.v

# El nombre del módulo Verilog de nivel superior
TOPLEVEL = dff

# El nombre del archivo Python que contiene el test pyuvm (sin .py)
MODULE = test_dff

# Incluir las reglas estándar de cocotb para simulación
include $(shell cocotb-config --makefiles)/Makefile.sim
