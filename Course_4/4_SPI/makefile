TOPLEVEL_LANG ?= verilog

# Default simulator (override with: make SIM=verilator ...)
SIM ?= icarus

# Select which cocotb test module (Python file without .py) to run
# Usage:
#   make TEST=spi_master_tb
#   make TEST=master_slave_tb
TEST ?= spi_master_tb
COCOTB_TEST_MODULES := $(TEST)

# Optional: keep cocotb logs compact
COCOTB_REDUCED_LOG_FMT ?= 1

# Enable waveform dump (if supported by the simulator)
WAVES ?= 1

# Select TOPLEVEL + sources based on the chosen test
ifeq ($(TEST),spi_master_tb)
TOPLEVEL := SPI_MASTER
VERILOG_SOURCES := $(shell pwd)/SPI_MASTER.sv
else ifeq ($(TEST),master_slave_tb)
TOPLEVEL := master_slave
VERILOG_SOURCES := $(shell pwd)/SPI_MASTER.sv $(shell pwd)/SPI_SLAVE.sv $(shell pwd)/master_slave.sv
else
$(error Unknown TEST='$(TEST)'. Valid values: spi_master_tb, master_slave_tb)
endif

# Note (Surfer): Icarus dumps enum values as bits in .fst.
# To display `state_type` as text in Surfer, use the mapping translator in:
#   .surfer/mappings/spi_master_state.map

ifeq ($(filter help,$(MAKECMDGOALS)),)
include $(shell cocotb-config --makefiles)/Makefile.sim
endif

.PHONY: test_all
test_all:
	$(MAKE) TEST=spi_master_tb
	$(MAKE) TEST=master_slave_tb

.PHONY: help
help:
	@echo "Targets:"
	@echo "  make TEST=spi_master_tb     # Run SPI master-only test"
	@echo "  make TEST=master_slave_tb   # Run master-slave integration test"
	@echo "  make test_all               # Run both tests"
	@echo "  make clean                  # Cleanup build artifacts"

.PHONY: clean
clean::
	rm -rf __pycache__
	rm -rf sim_build
	rm -rf results.xml
	rm -rf *.vcd
	rm -rf *.log