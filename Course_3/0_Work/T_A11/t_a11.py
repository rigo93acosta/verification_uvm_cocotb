class NumberManipulator:

    def __init__(self):
        self.data_member = 10
    
    def set_datam(self, value):
        self.data_member = value

    def get_sqdatam(self):
        return self.data_member ** 2
    
if __name__ == "__main__":

    number_manipulator = NumberManipulator()
    number_manipulator.set_datam(45)
    print(number_manipulator.get_sqdatam())