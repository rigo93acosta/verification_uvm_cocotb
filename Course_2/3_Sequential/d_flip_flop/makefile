TOPLEVEL_LANG ?= verilog
SIM ?= icarus
VERILOG_SOURCES = $(shell pwd)/d_ff.sv
TOPLEVEL := top # Verilog or SystemVerilog TOP file module name
COCOTB_TEST_MODULES   := d_ff_tb # Python file name


include $(shell cocotb-config --makefiles)/Makefile.sim