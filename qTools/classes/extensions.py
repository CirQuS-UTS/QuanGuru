from qTools.classes.QSys import Qubit


# below is an example of the idea for this script
# if you call an instance of QuantumSystem.x(arg)
# it will execute this function
# an additional use would be to decorate x (a func)
def maFnc(x):
    print(x)

Qubit.x = maFnc