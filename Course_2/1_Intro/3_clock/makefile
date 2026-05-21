TOPLEVEL_LANG ?= verilog
SIM ?= questa
VERILOG_SOURCES = $(shell pwd)/top_clock.sv
TOPLEVEL := top # Verilog or SystemVerilog TOP file module name
COCOTB_TEST_MODULES   := top_tb # Python file name
WAVES = 1
ifeq ("$(SIM)", "questa")
    # Usamos comandos nativos de tcl para abrir un archivo vcd y agregar las señales
    EXTRA_ARGS += -do "vcd file sim_build/waves.vcd; vcd add -r /*; run -all; quit"
endif
include $(shell cocotb-config --makefiles)/Makefile.sim
