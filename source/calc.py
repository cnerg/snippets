import math

def arith_op(a, b, op):
    if op == "+":
        c = a+b
    elif op == '-':
        c = a-b
    else:
        raise NotImplementedError
    return c

def circle_area(r):
    return math.pi*r**2
