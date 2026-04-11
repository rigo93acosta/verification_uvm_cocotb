TOPLEVEL_LANG ?= verilog
SIM ?= icarus
# VERILOG_SOURCES = $(shell pwd)/spi.sv # Solution course file
# VERILOG_SOURCES = $(shell pwd)/spi_my.sv # My implementation file
TOPLEVEL := SPI # Verilog or SystemVerilog TOP file module name
# Then using master & slave testbenches descommented
VERILOG_SOURCES += $(shell pwd)/SPI_MASTER.sv
#VERILOG_SOURCES += $(shell pwd)/top.sv
TOPLEVEL := SPI_MASTER
# TOPLEVEL := TOP
COCOTB_TEST_MODULES   := spi_master_tb # Python file name
# Then using master & slave testbenches descommented
# COCOTB_TEST_MODULES   := top_tb # Python file name
WAVES := 1

# Note (Surfer): Icarus dumps enum values as bits in .fst.
# To display `state_type` as text in Surfer, use the mapping translator in:
#   .surfer/mappings/spi_master_state.map

include $(shell cocotb-config --makefiles)/Makefile.sim