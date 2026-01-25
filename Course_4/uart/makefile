TOPLEVEL_LANG ?= verilog
SIM ?= icarus
VERILOG_SOURCES = $(shell pwd)/uart.sv
TOPLEVEL := UART # Verilog or SystemVerilog TOP file module name
COCOTB_TEST_MODULES   := uart_tb # Python file name

include $(shell cocotb-config --makefiles)/Makefile.sim
