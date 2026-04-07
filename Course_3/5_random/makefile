TOPLEVEL_LANG ?= verilog
SIM ?= icarus
VERILOG_SOURCES = $(shell pwd)/mult.sv
TOPLEVEL := mul
COCOTB_TEST_MODULES   := mult_tb # Python file name
WAVES = 1

include $(shell cocotb-config --makefiles)/Makefile.sim