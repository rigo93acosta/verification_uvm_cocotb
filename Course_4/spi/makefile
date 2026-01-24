TOPLEVEL_LANG ?= verilog
SIM ?= icarus
# VERILOG_SOURCES = $(shell pwd)/spi.sv # Solution course file
VERILOG_SOURCES = $(shell pwd)/spi_my.sv # My implementation file
TOPLEVEL := SPI # Verilog or SystemVerilog TOP file module name
COCOTB_TEST_MODULES   := spi_tb # Python file name

include $(shell cocotb-config --makefiles)/Makefile.sim
