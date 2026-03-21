# Makefile for SPI ML Verification

# Defaults
SIM ?= icarus
TOPLEVEL_LANG ?= verilog

# Verilog sources
VERILOG_SOURCES = $(PWD)/spi_master.sv \
                  $(PWD)/spi_slave.sv \
                  $(PWD)/spi_top.sv

# Toplevel module
TOPLEVEL = spi_top

# Python test module
MODULE = test_spi_ml

# Cocotb parameters
COCOTB_HDL_TIMEUNIT = 1ns
COCOTB_HDL_TIMEPRECISION = 1ps

# Include cocotb's make rules
include $(shell cocotb-config --makefiles)/Makefile.sim

# Clean target
clean::
	rm -rf sim_build
	rm -rf __pycache__
	rm -f results.xml
	rm -f *.vcd
	rm -f *.fst

# Run all tests
.PHONY: all
all:
	@echo "Running SPI ML verification..."

# Run specific tests
.PHONY: test_ml
test_ml:
	$(MAKE) TESTCASE=test_spi_ml_verification

.PHONY: test_alternating
test_alternating:
	$(MAKE) TESTCASE=test_alternating_slaves

.PHONY: test_sequential
test_sequential:
	$(MAKE) TESTCASE=test_sequential_slave

# View waveforms
.PHONY: waves
waves:
	@if [ -f dump.vcd ]; then \
		gtkwave dump.vcd; \
	elif [ -f dump.fst ]; then \
		gtkwave dump.fst; \
	else \
		echo "No waveform file found"; \
	fi
