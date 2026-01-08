TOPLEVEL_LANG ?= verilog
SIM ?= icarus
VERILOG_SOURCES = $(shell pwd)/memory.sv
TOPLEVEL := top # Verilog or SystemVerilog TOP file module name
COCOTB_TEST_MODULES   := memory_tb # Python file name


include $(shell cocotb-config --makefiles)/Makefile.sim