import QuantumToolbox.operators as oper
import scipy.sparse as sp

# Hamiltonian & Initial State #


def Hamiltonians(obj, resonatorDim):
    obj.resonatorDimension = resonatorDim
    obj.HamiltonianCavity = sp.kron(oper.number(resonatorDim),
                                    oper.identity(2), format='csc')
    obj.HamiltonianQubit = sp.kron(oper.identity(resonatorDim),
                                   oper.number(2), format='csc')
    obj.couplingHamiltonian = \
        sp.kron(oper.create(resonatorDim), oper.sigmax(), format='csc') \
        + sp.kron(oper.destroy(resonatorDim), oper.sigmax(), format='csc')
    obj.couplingJC = \
        sp.kron(oper.create(resonatorDim), oper.destroy(2), format='csc') \
        + sp.kron(oper.destroy(resonatorDim), oper.create(2), format='csc')
    obj.sigmaX = sp.kron(oper.identity(resonatorDim),
                         oper.sigmax(), format='csc')
    return obj
