import os
from pathlib import Path
from cocotb_tools.runner import get_runner


def test_runner_mux() -> None:
    sim_env = os.getenv("SIM", "verilator").lower()

    # map common names to the runner identifiers
    sim_map = {
        "verilator": "verilator",
        "icarus": "icarus",
        "iverilog": "icarus",
        "questa": "questa",
        "modelsim": "questa",
    }

    if sim_env not in sim_map:
        raise ValueError(
            f"Unsupported SIM '{sim_env}'. Supported: {', '.join(sorted(sim_map.keys()))}"
        )

    sim = sim_map[sim_env]

    proj_path = Path(__file__).resolve().parent

    sources = [proj_path / "mux.sv"]

    runner = get_runner(sim)

    # select safe build args per simulator
    if sim == "verilator":
        build_args = ["--trace", "--trace-fst", "--trace-structs"]
    else:
        build_args = []

    runner.build(
        sources=sources,
        hdl_toplevel="mux",
        always=True,
        timescale=["1ns", "1ns"],
        build_args=build_args,
        waves=True,
    )

    runner.test(
        hdl_toplevel="mux",
        test_module="mux_tb",
        waves=True,
    )

    # After the run, if Questa produced a WLF file, try to convert it to VCD/FST
    if sim == "questa":
        from shutil import which
        import subprocess

        build_dir = proj_path / "sim_build"
        wlf = build_dir / "vsim.wlf"
        vcd = build_dir / "dump.vcd"
        fst = build_dir / "dump.fst"

        if wlf.exists():
            wlf2vcd = which("wlf2vcd")
            if wlf2vcd:
                try:
                    subprocess.run([wlf2vcd, "-o", str(vcd), str(wlf)], check=True)
                except subprocess.CalledProcessError:
                    pass

            vcd2fst = which("vcd2fst") or which("vcd2fst.pl") or which("vcd2fst.py")
            if vcd.exists() and vcd2fst:
                try:
                    subprocess.run([vcd2fst, str(vcd), str(fst)], check=True)
                except subprocess.CalledProcessError:
                    pass


if __name__ == "__main__":
    test_runner_mux()
