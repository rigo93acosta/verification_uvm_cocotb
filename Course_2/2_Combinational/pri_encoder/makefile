TOPLEVEL_LANG ?= verilog
SIM ?= icarus
VERILOG_SOURCES = $(shell pwd)/pri_enc.sv
TOPLEVEL := pri_enc # Verilog or SystemVerilog TOP file module name
MODULE   := pri_enc_tb # Python file name
# Ensure compatibility with simulator makefiles that expect COCOTB_TEST_MODULES
# (some simulators no longer map MODULE -> COCOTB_TEST_MODULES automatically)
COCOTB_TEST_MODULES ?= $(MODULE)
WAVES = 1
ifeq ($(SIM), "questa")
	
	    EXTRA_ARGS += -do "vcd file sim_build/waves.vcd; vcd add -r /*; run -all; quit"

endif

include $(shell cocotb-config --makefiles)/Makefile.sim