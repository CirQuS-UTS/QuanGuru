from qTools.QuantumToolbox.operators import sigmaz, sigmax, sigmay, identity
from numpy import cos, sin

def xRotation(angle, sparse=True):
    rotUnitary = ((cos(angle)*identity(2, sparse))+(sin(angle)*sigmax(sparse=sparse)))
    return rotUnitary

def yRotation(angle, sparse=True):
    rotUnitary = ((cos(angle)*identity(2, sparse))+(sin(angle)*sigmay(sparse=sparse)))
    return rotUnitary

def zRotation(angle, sparse=True):
    rotUnitary = ((cos(angle)*identity(2, sparse))+(sin(angle)*sigmaz(sparse=sparse)))
    return rotUnitary

def qubRotation(xyz=str, angle=float, sparse=True):
    if xyz.lower() == 'x':
        rotUnitary = xRotation(angle, sparse)
    elif xyz.lower() == 'y':
        rotUnitary = yRotation(angle, sparse)
    elif xyz.lower() == 'z':
        rotUnitary = zRotation(angle, sparse)
    else:
        print(xyz + ' is not supported')
    return rotUnitary

