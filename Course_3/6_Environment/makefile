TOPLEVEL_LANG ?= verilog
SIM ?= icarus
VERILOG_SOURCES = $(shell pwd)/top.sv
# Verilog/SystemVerilog top module name.
TOPLEVEL := top
# Python test module.
COCOTB_TEST_MODULES := top_tb
# Enable waveform dumping for the Icarus cocotb makefile.
WAVES := 1

include $(shell cocotb-config --makefiles)/Makefile.sim