import cProfile

a = range(0, 10000000)
b = range(10000000, 20000000)

def toto(a, b):
    a.add(5)
    b[3] = 'c'

a = set([1, 2, 3])
b = {1: 'a', 2: 'b'}

toto(a, b)
print(a)
print(b)