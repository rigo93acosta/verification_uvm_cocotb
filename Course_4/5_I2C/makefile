TOPLEVEL_LANG ?= verilog
SIM ?= icarus
VERILOG_SOURCES = $(shell pwd)/i2c.sv
TOPLEVEL := i2c # Verilog or SystemVerilog TOP file module name
COCOTB_TEST_MODULES   := i2c_tb # Python file name
WAVES := 1

include $(shell cocotb-config --makefiles)/Makefile.sim
