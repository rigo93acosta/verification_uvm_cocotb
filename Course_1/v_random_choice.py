import random as rnd

"""
choices -> Retorna um elemento aleatorio de una lista
weight -> Peso para cada elemento da lista
k -> Cantidad de elementos a ser retornados
"""

arr = [0, 1, 2, 3]
for i in range(10):
    state = rnd.choices(arr, weights=[1, 5, 5, 5], k=2)
    print(f"{state}")


