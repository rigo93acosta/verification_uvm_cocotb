TOPLEVEL_LANG ?= verilog
SIM ?= icarus
VERILOG_SOURCES = $(shell pwd)/half_adder.sv
TOPLEVEL := top
COCOTB_TEST_MODULES   := half_adder_tb # Python file name
WAVES = 1

include $(shell cocotb-config --makefiles)/Makefile.sim