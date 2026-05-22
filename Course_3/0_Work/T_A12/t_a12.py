class TemperatureConverter:

    def __init__(self):
        self.t_celsius = 0

    def set_temperature(self, celsius:float) -> None:
        self.t_celsius = celsius

    def get_temperature_in_fahrenheit(self) -> float:
        return (self.t_celsius * 9/5) + 32

if __name__ == "__main__":

    temp_converter = TemperatureConverter()
    temp_converter.set_temperature(25.5)
    print(temp_converter.get_temperature_in_fahrenheit())