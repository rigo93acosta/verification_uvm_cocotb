import os
import shutil
import subprocess
from pathlib import Path

from cocotb_tools.runner import get_runner


def _try_run(cmd):
    try:
        subprocess.run(
            cmd, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
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


def test_d_ff():
    sim = os.getenv("SIM", "icarus").lower()
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
    sources = [
        proj_path / "d_ff.sv",
    ]

    runner = get_runner(sim_map[sim])
    build_args = (
        ["--trace", "--trace-fst", "--trace-structs"]
        if sim_map[sim] == "verilator"
        else []
    )

    runner.build(
        sources=sources,
        hdl_toplevel="d_ff",
        timescale=["1ns", "1ns"],
        build_args=build_args,
        waves=True,
        always=True,
    )

    runner.test(
        hdl_toplevel="d_ff",
        test_module="d_ff_tb",
        waves=True,
    )

    if sim_map[sim] == "questa":
        _post_process_questa(proj_path / "sim_build")
