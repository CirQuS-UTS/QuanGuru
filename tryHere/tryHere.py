from classes.parameterObj import ParamObj

o = ParamObj('o')
b = ParamObj('b')

print(o.times)
o.finalTime = 2
o.TrotterStep = 0.002
def func():
    print('x')
def gunc():
    print('y')
"""o.addMethod(func)
b.addMethod(gunc)

o.func('x')
b.gunc('y')
o.func('b')"""

o.unitary = func
b.unitary = gunc

o.unitary()
b.unitary()
o.unitary()

print(o.times)
print(o.TrotterTimes)