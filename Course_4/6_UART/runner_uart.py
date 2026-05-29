import os
import shutil
import subprocess
from pathlib import Path

from cocotb_tools.runner import get_runner


def _parse_baud_rates(raw_value):
    if not raw_value:
        return [9600]

    parts = raw_value.replace(" ", ",").split(",")
    baud_rates = []
    for part in parts:
        if not part:
            continue
        baud_rates.append(int(part))

    if not baud_rates:
        return [9600]

    return baud_rates


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


def test_uart():
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
        proj_path / "uart.sv",
    ]
    baud_rates = _parse_baud_rates(os.getenv("BAUD_RATES"))

    runner = get_runner(sim_map[sim])
    if sim_map[sim] == "verilator":
        build_args = ["--trace", "--trace-fst", "--trace-structs", "-I", str(proj_path)]
    elif sim_map[sim] == "icarus":
        build_args = ["-I", str(proj_path)]
    else:
        build_args = []

    for baud_rate in baud_rates:
        build_dir = proj_path / "sim_build" / f"baud_{baud_rate}"
        runner.build(
            sources=sources,
            hdl_toplevel="uart",
            timescale=["1ns", "1ps"],
            build_args=build_args,
            parameters={"baud_rate": baud_rate},
            waves=True,
            always=True,
            build_dir=build_dir,
        )

        runner.test(
            hdl_toplevel="uart",
            test_module="uart_tb",
            waves=True,
            build_dir=build_dir,
            extra_env={"BAUD_RATE": str(baud_rate)},
        )

        if sim_map[sim] == "questa":
            _post_process_questa(build_dir)
