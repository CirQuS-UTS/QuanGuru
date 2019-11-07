import QuantumToolbox.operators as oper
import scipy.sparse as sp

# Hamiltonians #


def Hamiltonians(obj):
    resonatorDimension = obj.systemParameters.resonatorDimension
    obj.HamiltonianCavity = sp.kron(oper.number(resonatorDimension),oper.identity(2), format='csc')
    obj.HamiltonianQubit = sp.kron(oper.identity(resonatorDimension),oper.sigmaz(), format='csc')
    obj.couplingHamiltonian = (sp.kron(oper.create(resonatorDimension), oper.sigmax(), format='csc')
                               + sp.kron(oper.destroy(resonatorDimension), oper.sigmax(), format='csc'))
    obj.couplingJC = (sp.kron(oper.create(resonatorDimension), oper.destroy(2), format='csc')
                      + sp.kron(oper.destroy(resonatorDimension), oper.create(2), format='csc'))
    obj.sigmaX = sp.kron(oper.identity(resonatorDimension),oper.sigmax(), format='csc')
    return obj
