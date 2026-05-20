TOPLEVEL_LANG ?= verilog
SIM ?= verilator
VERILOG_SOURCES = $(shell pwd)/fifo.sv
TOPLEVEL := FIFO # Verilog or SystemVerilog TOP file module name
COCOTB_TEST_MODULES   := fifo_tb # Python file name
WAVES := 1
COMPILE_ARGS += --coverage --coverage-line --coverage-toggle

include $(shell cocotb-config --makefiles)/Makefile.sim
