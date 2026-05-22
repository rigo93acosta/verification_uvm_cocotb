import copy
from dataclasses import dataclass

@dataclass
class Person:
    name: str | None = None

    def set_name(self, name: str) -> None:
        self.name = str(name)

    def get_name(self) -> str | None:
        return self.name
    
def main():

    person_1 = Person()
    person_1.set_name("Alice")
    
    person_2 = person_1
    print(f"Person 2 name: {person_2.get_name()}")
    person_2.set_name("Bob")
    print(f"Person 1 name: {person_1.get_name()}")

    person_3 = Person()
    person_3.set_name("Charlie")

    person_4 = copy.deepcopy(person_3)
    print(f"Person 4 name: {person_4.get_name()}")
    person_4.set_name("David")
    print(f"Person 3 name: {person_3.get_name()}")


if __name__ == "__main__":
    main()
