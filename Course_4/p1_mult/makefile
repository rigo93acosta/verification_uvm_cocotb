TOPLEVEL_LANG ?= verilog
SIM ?= icarus
VERILOG_SOURCES = $(shell pwd)/mult.sv
TOPLEVEL := mult # Verilog or SystemVerilog TOP file module name
COCOTB_TEST_MODULES   := mult_tb # Python file name

include $(shell cocotb-config --makefiles)/Makefile.sim