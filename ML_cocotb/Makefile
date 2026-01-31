# Makefile
SIM ?= icarus
TOPLEVEL_LANG ?= verilog
VERILOG_SOURCES += filter.v
TOPLEVEL = filter
# MODULE = test_fir_ml # Classifier testbench module
# MODULE = test_fir_ml_regressor # Regressor testbench module
MODULE = test_fir_ml_memory # Temporal ML testbench module


include $(shell cocotb-config --makefiles)/Makefile.sim