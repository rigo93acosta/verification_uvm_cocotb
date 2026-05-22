class StringManipulator:
    def __init__(self):
        self.data_string = ""

    def set_string(self, string: str) -> None:
        self.data_string += string

    def get_string_length(self) -> int:
        return len(self.data_string)


if __name__ == "__main__":
    string_manipulator = StringManipulator()
    string_manipulator.set_string("Hello, World!")
    print(f"String: {string_manipulator.data_string}")
    print(f"String Length: {string_manipulator.get_string_length()}")
