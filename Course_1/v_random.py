import random

a = random.randint(0, 15)
print(f"Random integer between 0 and 15: {a}")

random.seed(1)
b = random.randint(0, 15)
print(b)

c = random.random()
"""
El "estado" es un objeto interno complejo que contiene la configuración actual del generador de números.

getstate(): Toma una "foto" de en qué parte de la secuencia aleatoria se encuentra el programa justo ahora.

¿Para qué se usa? Si guardas el estado en state0, puedes generar 100 números y luego usar random.setstate(state0) para "volver en el tiempo" y generar exactamente esos mismos 100 números otra vez, sin importar si habías usado una semilla al principio o no.
"""

state0 = random.getstate()
print(f"Random float between 0 and 1: {c}")

c = random.random()
state1 = random.getstate()
print(f"Random float between 0 and 1: {c}")

c = random.random()
print(f"Random float between 0 and 1: {c}")


random.setstate(state1)
c = random.random()
print(f"Random float between 0 and 1 (after resetting state): {c}")

for i in range(15):
    a = random.getrandbits(4)
    print(f"Random 8 bits as integer: {a}")

print("Resetting state to state0")

random.setstate(state0)
for i in range(15):
    a = random.getrandbits(4)
    print(f"Random 8 bits as integer: {a}")

print("Resetting state to state1")
random.setstate(state1)
for i in range(15):
    a = random.getrandbits(4)
    print(f"Random 8 bits as integer: {a}")