def check_essential_libraries():
    libraries = ["cocotb", "pandas", "pytest", "pyuvm"]
    all_present = True
    for lib in libraries:
        try:
            __import__(lib)
            print(f"{lib} is installed.")
        except ImportError:
            print(f"{lib} is not installed.")
            all_present = False
    return all_present

def main():
    print("Hello from uvm-ver!")
    print("Checking essential libraries...")
    if check_essential_libraries():
        print("All essential libraries are available.")
    else:
        print("Some essential libraries are missing. Please install them.")


if __name__ == "__main__":
    main()
