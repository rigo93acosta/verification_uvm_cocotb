import os
import sys
import shutil
import subprocess
from pathlib import Path
from cocotb_tools.runner import get_runner


def test_dff_synthesis():

    sim_env = os.getenv("SIM", "icarus").lower()
    sim_map = {
        "verilator": "verilator",
        "iverilog": "icarus",
        "icarus": "icarus",
        "questa": "questa",
        "modelsim": "questa",
    }
    if sim_env not in sim_map:
        raise ValueError(f"SIM not supported: {sim_env}")
    sim = sim_map[sim_env]

    proj_path = Path(__file__).resolve().parent
    sources = [proj_path / "dff_synth.v"]

    # obtener datadir de Yosys
    datdir = None
    yc = shutil.which("yosys-config") or shutil.which("yosys")
    if yc:
        try:
            datdir = subprocess.run(
                [yc, "--datdir"], check=True, capture_output=True, text=True
            ).stdout.strip()
        except Exception:
            datdir = None

    if not datdir and Path("/usr/share/yosys").exists():
        datdir = "/usr/share/yosys"

    if not datdir:
        print(
            "ERROR: no se encontró datdir de Yosys (instala yosys o pone yosys-config en PATH)"
        )
        sys.exit(1)

    simlib = Path(datdir) / "simlib.v"
    if not simlib.exists():
        print(f"ERROR: simlib.v no encontrado en {simlib}")
        sys.exit(1)
    sources.append(simlib)

    runner = get_runner(sim)
    build_args = (
        ["--trace", "--trace-fst", "--trace-structs"] if sim == "verilator" else []
    )
    runner.build(
        sources=sources,
        hdl_toplevel="dff",
        build_dir=proj_path / "sim_build_synth",
        timescale=["1ns", "1ps"],
        build_args=build_args,
        waves=(sim == "verilator"),
    )

    runner.test(
        test_module="dff_tb",
        hdl_toplevel="dff",
        testcase="test",
        build_dir=proj_path / "sim_build_synth",
        timescale=("1ns", "1ps"),
    )


if __name__ == "__main__":
    test_dff_synthesis()
