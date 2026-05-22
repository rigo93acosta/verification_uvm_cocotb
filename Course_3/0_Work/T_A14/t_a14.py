from dataclasses import dataclass


@dataclass
class Transaction:
    a: int
    b: int
    y: int = 0
    done: bool = False


if __name__ == "__main__":

    t = Transaction(a=1, b=2)
    print(f"Example Transaction: {t}")