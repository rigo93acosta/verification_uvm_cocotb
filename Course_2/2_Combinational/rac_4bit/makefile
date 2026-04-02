TOPLEVEL_LANG ?= verilog
SIM ?= icarus
VERILOG_SOURCES = $(shell pwd)/half_adder.sv
TOPLEVEL := top # Verilog or SystemVerilog TOP file module name
COCOTB_TEST_MODULES   := half_adder_tb # Python file name

include $(shell cocotb-config --makefiles)/Makefile.sim