TOPLEVEL_LANG ?= verilog
SIM ?= icarus
VERILOG_SOURCES = $(shell pwd)/top_tb.sv
TOPLEVEL := top
COCOTB_TEST_MODULES   := top_tb
WAVES ?= 1
COCOTB_WAVEFORM_VIEWER ?= gtkwave
GUI ?= 1

include $(shell cocotb-config --makefiles)/Makefile.sim
# Abre Surfer (o GTKWave) después de la simulación
.PHONY: view
view:
	@if command -v surfer >/dev/null 2>&1; then \
		surfer sim_build/$(TOPLEVEL).fst & \
	else \
		$(COCOTB_WAVEFORM_VIEWER) sim_build/$(TOPLEVEL).fst & \
	fi