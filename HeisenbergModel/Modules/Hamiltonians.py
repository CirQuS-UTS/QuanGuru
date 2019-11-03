import QuantumToolbox.operators as qOps
import scipy.sparse as sp

def twoQubitHeisenberg(obj):
    j = obj.systemParameters.g
    obj.hXY = (j / 2) * (sp.kron(qOps.sigmax(), qOps.sigmax(), format='csc') + sp.kron(qOps.sigmay(), qOps.sigmay(), format='csc'))
    obj.hXZ = (j / 2) * (sp.kron(qOps.sigmax(), qOps.sigmax(), format='csc') + sp.kron(qOps.sigmaz(), qOps.sigmaz(), format='csc'))
    obj.hYZ = (j / 2) * (sp.kron(qOps.sigmay(), qOps.sigmay(), format='csc') + sp.kron(qOps.sigmaz(), qOps.sigmaz(), format='csc'))
    obj.hH = j * (sp.kron(qOps.sigmay(), qOps.sigmay(), format='csc') + sp.kron(qOps.sigmaz(), qOps.sigmaz(), format='csc')
                  + sp.kron(qOps.sigmax(),qOps.sigmax(), format='csc'))
    return obj


def threeQubitHeisenberg(obj):
    j = obj.systemParameters.g
    obj.hXY3 = (j / 2) * (sp.kron(sp.kron(qOps.sigmax(), qOps.sigmax(), format='csc'), qOps.identity(2), format='csc')
                          + sp.kron(sp.kron(qOps.sigmay(), qOps.sigmay(), format='csc'), qOps.identity(2), format='csc'))
    obj.h1XY = (j / 2) * (sp.kron(sp.kron(qOps.identity(2), qOps.sigmax(), format='csc'), qOps.sigmax(), format='csc')
                          + sp.kron(sp.kron(qOps.identity(2), qOps.sigmay(), format='csc'), qOps.sigmay(), format='csc'))
    obj.hXZ3 = (j / 2) * (sp.kron(sp.kron(qOps.sigmax(), qOps.sigmax(), format='csc'), qOps.identity(2), format='csc')
                          + sp.kron(sp.kron(qOps.sigmaz(), qOps.sigmaz(), format='csc'), qOps.identity(2), format='csc'))
    obj.h1XZ = (j / 2) * (sp.kron(sp.kron(qOps.identity(2), qOps.sigmax(), format='csc'), qOps.sigmax(), format='csc')
                          + sp.kron(sp.kron(qOps.identity(2), qOps.sigmaz(), format='csc'), qOps.sigmaz(), format='csc'))
    obj.hYZ3 = (j / 2) * (sp.kron(sp.kron(qOps.sigmay(), qOps.sigmay(), format='csc'), qOps.identity(2), format='csc')
                          + sp.kron(sp.kron(qOps.sigmaz(), qOps.sigmaz(), format='csc'), qOps.identity(2), format='csc'))
    obj.h1YZ = (j / 2) * (sp.kron(sp.kron(qOps.identity(2), qOps.sigmay(), format='csc'), qOps.sigmay(), format='csc')
                          + sp.kron(sp.kron(qOps.identity(2), qOps.sigmaz(), format='csc'), qOps.sigmaz(), format='csc'))
    obj.hH3 = j*(sp.kron(sp.kron(qOps.sigmay(),qOps.sigmay(), format='csc'), qOps.identity(2), format='csc') +
                 sp.kron(sp.kron(qOps.identity(2),qOps.sigmay(), format='csc'), qOps.sigmay(), format='csc') +
                 sp.kron(sp.kron(qOps.sigmax(), qOps.sigmax(), format='csc'), qOps.identity(2), format='csc') +
                 sp.kron(sp.kron(qOps.identity(2), qOps.sigmax(), format='csc'), qOps.sigmax(), format='csc') +
                 sp.kron(sp.kron(qOps.sigmaz(), qOps.sigmaz(), format='csc'), qOps.identity(2), format='csc') +
                 sp.kron(sp.kron(qOps.identity(2), qOps.sigmaz(), format='csc'), qOps.sigmaz(), format='csc'))
    return obj