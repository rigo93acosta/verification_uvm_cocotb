TOPLEVEL_LANG ?= verilog
SIM ?= icarus
VERILOG_SOURCES = $(shell pwd)/d_ff.sv
TOPLEVEL := top
COCOTB_TEST_MODULES   := d_ff_tb # Python file name
WAVES = 1
GUI = 1

# NOTE:
# - With Icarus, cocotb commonly honors WAVES=1 to emit a VCD.
# - With Verilator, waveform dumping is typically controlled by VERILATOR_TRACE/TRACE.
ifeq ($(SIM),verilator)
VERILATOR_TRACE ?= 1
TRACE ?= 1
endif

include $(shell cocotb-config --makefiles)/Makefile.sim