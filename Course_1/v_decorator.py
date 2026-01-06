def dec(fun):
    def wrapper():
        print("Before calling the function.")
        fun()
        print("After calling the function.")
    return wrapper

@dec
def say_hello():
    print("Hello!")

say_hello()