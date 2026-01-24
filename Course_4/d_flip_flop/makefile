TOPLEVEL_LANG ?= verilog
SIM ?= icarus
VERILOG_SOURCES = $(shell pwd)/dff.sv
TOPLEVEL := dff # Verilog or SystemVerilog TOP file module name
COCOTB_TEST_MODULES   := dff_tb # Python file name

include $(shell cocotb-config --makefiles)/Makefile.sim
