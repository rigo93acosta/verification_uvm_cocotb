## Binary Types in Python
var6 = b'255' #8-bit : 0 - 255
print(var6)

## Bytearray : Mutable sequence of bytes
var7 = bytearray([1,2,255,4])
print(var7)

## Memory View : Access the internal data of an object
mem = memoryview(var7)
print(mem[2])

mem[2] = 128
print(var7)
