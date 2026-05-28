import os
import shutil
import subprocess
from pathlib import Path

from cocotb_tools.runner import get_runner


def _try_run(cmd):
    try:
        subprocess.run(cmd, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass


def _post_process_questa(sim_build_dir):
    wlf = sim_build_dir / "vsim.wlf"
    if not wlf.exists():
        return

    vcd = sim_build_dir / "vsim.vcd"
    if shutil.which("wlf2vcd"):
        _try_run(["wlf2vcd", "-o", str(vcd), str(wlf)])

    fst = sim_build_dir / "vsim.fst"
    if vcd.exists() and shutil.which("vcd2fst"):
        _try_run(["vcd2fst", str(vcd), str(fst)])


def _get_configs(proj_path, test_module):
    configs = {
        "spi_master_tb": {
            "hdl_toplevel": "SPI_MASTER",
            "sources": [
                proj_path / "SPI_MASTER.sv",
            ],
        },
        "master_slave_tb": {
            "hdl_toplevel": "master_slave",
            "sources": [
                proj_path / "master_slave.sv",
                proj_path / "SPI_MASTER.sv",
                proj_path / "SPI_SLAVE.sv",
            ],
        },
    }

    if test_module == "all":
        return [(name, configs[name]) for name in sorted(configs.keys())]

    if test_module not in configs:
        options = ", ".join(sorted(configs.keys()))
        raise ValueError(f"Unknown TEST_MODULE '{test_module}'. Options: {options}")

    return [(test_module, configs[test_module])]


def test_spi_unified():
    sim = os.getenv("SIM", "verilator").lower()
    sim_map = {
        "verilator": "verilator",
        "iverilog": "icarus",
        "icarus": "icarus",
        "questa": "questa",
        "modelsim": "questa",
    }
    if sim not in sim_map:
        raise ValueError(f"SIM not supported: {sim}")

    proj_path = Path(__file__).resolve().parent
    test_module = os.getenv("TEST_MODULE", "master_slave_tb")
    config_items = _get_configs(proj_path, test_module)

    runner = get_runner(sim_map[sim])
    build_args = ["--trace", "--trace-fst", "--trace-structs"] if sim_map[sim] == "verilator" else []

    for module_name, config in config_items:
        runner.build(
            sources=config["sources"],
            hdl_toplevel=config["hdl_toplevel"],
            timescale=["1ns", "1ns"],
            build_args=build_args,
            waves=True,
            always=True,
        )

        runner.test(
            hdl_toplevel=config["hdl_toplevel"],
            test_module=module_name,
            waves=True,
        )

    if sim_map[sim] == "questa":
        _post_process_questa(proj_path / "sim_build")


if __name__ == "__main__":
    test_spi_unified()
