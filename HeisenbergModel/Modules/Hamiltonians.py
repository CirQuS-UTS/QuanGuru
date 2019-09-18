from QuantumToolbox.operators import sigmax,sigmaz,sigmay, identity
import scipy.sparse as sp

def twoQubitHeisenberg(obj):
    j = obj.g
    obj.hXY = (j / 2) * (sp.kron(sigmax(), sigmax(), format='csc') + sp.kron(sigmay(), sigmay(), format='csc'))
    obj.hXZ = (j / 2) * (sp.kron(sigmax(), sigmax(), format='csc') + sp.kron(sigmaz(), sigmaz(), format='csc'))
    obj.hYZ = (j / 2) * (sp.kron(sigmay(), sigmay(), format='csc') + sp.kron(sigmaz(), sigmaz(), format='csc'))
    obj.hH = j * (sp.kron(sigmay(), sigmay(), format='csc') + sp.kron(sigmaz(), sigmaz(), format='csc') + sp.kron(sigmax(),sigmax(), format='csc'))
    return obj


def threeQubitHeisenberg(obj):
    j = obj.g
    obj.hXY3 = (j / 2) * (sp.kron(sp.kron(sigmax(), sigmax(), format='csc'), identity(2), format='csc')
                          + sp.kron(sp.kron(sigmay(), sigmay(), format='csc'), identity(2), format='csc'))
    obj.h1XY = (j / 2) * (sp.kron(sp.kron(identity(2), sigmax(), format='csc'), sigmax(), format='csc')
                          + sp.kron(sp.kron(identity(2), sigmay(), format='csc'), sigmay(), format='csc'))
    obj.hXZ3 = (j / 2) * (sp.kron(sp.kron(sigmax(), sigmax(), format='csc'), identity(2), format='csc')
                          + sp.kron(sp.kron(sigmaz(), sigmaz(), format='csc'), identity(2), format='csc'))
    obj.h1XZ = (j / 2) * (sp.kron(sp.kron(identity(2), sigmax(), format='csc'), sigmax(), format='csc')
                          + sp.kron(sp.kron(identity(2), sigmaz(), format='csc'), sigmaz(), format='csc'))
    obj.hYZ3 = (j / 2) * (sp.kron(sp.kron(sigmay(), sigmay(), format='csc'), identity(2), format='csc')
                          + sp.kron(sp.kron(sigmaz(), sigmaz(), format='csc'), identity(2), format='csc'))
    obj.h1YZ = (j / 2) * (sp.kron(sp.kron(identity(2), sigmay(), format='csc'), sigmay(), format='csc')
                          + sp.kron(sp.kron(identity(2), sigmaz(), format='csc'), sigmaz(), format='csc'))
    obj.hH3 = j*(sp.kron(sp.kron(sigmay(),sigmay(), format='csc'), identity(2), format='csc') +
                 sp.kron(sp.kron(identity(2),sigmay(), format='csc'), sigmay(), format='csc') +
                 sp.kron(sp.kron(sigmax(), sigmax(), format='csc'), identity(2), format='csc') +
                 sp.kron(sp.kron(identity(2), sigmax(), format='csc'), sigmax(), format='csc') +
                 sp.kron(sp.kron(sigmaz(), sigmaz(), format='csc'), identity(2), format='csc') +
                 sp.kron(sp.kron(identity(2), sigmaz(), format='csc'), sigmaz(), format='csc'))
    return obj