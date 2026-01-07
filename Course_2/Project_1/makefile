TOPLEVEL_LANG ?= verilog
SIM ?= icarus
# VERILOG_SOURCES = $(shell pwd)/adder.sv
VERILOG_SOURCES = $(shell pwd)/sum.sv
# TOPLEVEL := mux # Verilog or SystemVerilog TOP file module name
TOPLEVEL := sum # Verilog or SystemVerilog TOP file module name
# COCOTB_TEST_MODULES   := adder_tb # Python file name
COCOTB_TEST_MODULES   := sum_tb # Python file name

include $(shell cocotb-config --makefiles)/Makefile.sim