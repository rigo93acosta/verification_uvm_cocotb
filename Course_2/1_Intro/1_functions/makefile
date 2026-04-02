TOPLEVEL_LANG ?= verilog
SIM ?= icarus
VERILOG_SOURCES = $(shell pwd)/top_tb.sv
TOPLEVEL := top
COCOTB_TEST_MODULES   := top_tb
WAVES ?= 1
COCOTB_WAVEFORM_VIEWER ?= gtkwave
GUI ?= 1

include $(shell cocotb-config --makefiles)/Makefile.sim
# Abre gtkwave después de la simulación
.PHONY: view
view:
	@surfer sim_build/$(TOPLEVEL).fst &