class Shape:
    def __init__(self, color):
        self.color = color

    def area(self):
        pass

    def display(self):
        print(
            f"Shape: {self.__class__.__name__} -- "
            f"color: {self.color} -- "
            f"Area: {self.area()}"
        )


class Circle(Shape):
    def __init__(self, color, radius):
        super().__init__(color)
        self.radius = radius

    def area(self):
        return 3.14 * self.radius**2


class Rectangle(Shape):
    def __init__(self, color, width, height):
        super().__init__(color)
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height


if __name__ == "__main__":
    circle = Circle("Red", 5)
    rectangle = Rectangle("Blue", 4, 6)

    circle.display()
    rectangle.display()
