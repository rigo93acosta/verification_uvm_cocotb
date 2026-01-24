TOPLEVEL_LANG ?= verilog
SIM ?= icarus
VERILOG_SOURCES = $(shell pwd)/fifo.sv
TOPLEVEL := FIFO # Verilog or SystemVerilog TOP file module name
COCOTB_TEST_MODULES   := fifo_tb # Python file name

include $(shell cocotb-config --makefiles)/Makefile.sim
