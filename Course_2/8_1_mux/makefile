TOPLEVEL_LANG ?= verilog
SIM ?= icarus
VERILOG_SOURCES = $(shell pwd)/mux.sv
TOPLEVEL := mux # Verilog or SystemVerilog TOP file module name
COCOTB_TEST_MODULES   := mux_tb # Python file name

include $(shell cocotb-config --makefiles)/Makefile.sim