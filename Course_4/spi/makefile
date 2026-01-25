TOPLEVEL_LANG ?= verilog
SIM ?= icarus
# VERILOG_SOURCES = $(shell pwd)/spi.sv # Solution course file
# VERILOG_SOURCES = $(shell pwd)/spi_my.sv # My implementation file
TOPLEVEL := SPI # Verilog or SystemVerilog TOP file module name
# Then using master & slave testbenches descommented
VERILOG_SOURCES += $(shell pwd)/top.sv
TOPLEVEL := TOP
# COCOTB_TEST_MODULES   := spi_tb # Python file name
# Then using master & slave testbenches descommented
COCOTB_TEST_MODULES   := top_tb # Python file name

include $(shell cocotb-config --makefiles)/Makefile.sim