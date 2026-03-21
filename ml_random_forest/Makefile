# Makefile for Random Forest ML-based Multiplier Verification

# Defaults
SIM ?= icarus
TOPLEVEL_LANG ?= verilog

# Verilog sources
VERILOG_SOURCES = $(PWD)/mult.sv

# Toplevel module
TOPLEVEL = mult

# Python test module
MODULE = test_mult_rf

# Include cocotb's make rules to take care of the simulator setup
include $(shell cocotb-config --makefiles)/Makefile.sim

# Clean target
clean::
	rm -rf sim_build
	rm -rf __pycache__
	rm -f results.xml
	rm -f *.vcd
	rm -f *.png

# Default target - just run the simulation
.PHONY: all
all:
	@echo "Running cocotb simulation..."

# Run specific test
.PHONY: test_rf
test_rf:
	$(MAKE) TESTCASE=test_mult_random_forest

.PHONY: test_edge
test_edge:
	$(MAKE) TESTCASE=test_edge_cases

.PHONY: test_exhaustive
test_exhaustive:
	$(MAKE) TESTCASE=test_exhaustive_small
