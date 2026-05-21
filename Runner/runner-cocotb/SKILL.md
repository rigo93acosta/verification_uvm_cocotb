---
name: runner-cocotb
description: "Create a Cocotb runner from an RTL + testbench layout. Use when: crear runner cocotb, runner cocotb, create cocotb runner, cocotb_tools.runner. Generates runner Python file based on SIM env and wave options."
argument-hint: "toplevel, test_module, sources, sim (verilator/icarus/questa), waves"
---

# Cocotb Runner Creator

## When to Use
- Need a runner.py using cocotb_tools.runner
- Want SIM env selection and wave dumps
- Convert WLF to VCD/FST for Questa

## Inputs to Collect
- Project root path
- RTL sources (ordered list)
- Top-level module name
- Top RTL file name (used to derive runner file name)
- Existing Cocotb test module name (python file without .py)
- Preferred default simulator (verilator/icarus/questa)
- Timescale and wave options

## Procedure
1. Normalize SIM with map: verilator/iverilog/icarus/questa/modelsim.
2. Build sources list with Path(...).
3. Derive the runner file name from the top RTL file name (e.g., top.sv):
	- runner file: runner_<rtl_name>.py
4. In the runner, define def test_<rtl_name>(): as the entrypoint (no main()).
5. Keep the existing testbench filename; do not rename or wrap it.
6. Create runner via get_runner.
7. Build with waves=True, timescale, build_args for verilator.
8. Test with hdl_toplevel and the provided test_module.
9. If sim is questa: convert sim_build/vsim.wlf using wlf2vcd -o vcd_output wlf_input and vcd2fst; ignore failures.

## Output
- New runner file (default: runner_<rtl_name>.py) with def test_<rtl_name>()
- No changes to the existing testbench file
- Optional note about how to run

## Template
- Use [runner template](./assets/runner_template.py)
