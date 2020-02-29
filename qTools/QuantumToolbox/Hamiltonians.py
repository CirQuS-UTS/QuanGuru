import qTools.QuantumToolbox.operators as ops
import scipy.sparse as sp

def cavQubFreeHam(cavFreq,qubFreq,cavDim):
    cavHam = cavFreq * sp.kron(ops.number(cavDim), ops.identity(2), format='csc')
    qubHam = qubFreq * sp.kron(ops.identity(cavDim), ops.sigmaz(), format='csc')
    return cavHam, qubHam


def RabiHam(cavFreq, qubFreq, g, cavDim):
    cavHam, qubHam = cavQubFreeHam(cavFreq,qubFreq,cavDim)
    couplingRabi = g*(sp.kron(ops.create(cavDim) + ops.destroy(cavDim), ops.sigmax(), format='csc'))

    rabiHam = cavHam + qubHam + couplingRabi
    return rabiHam


def JCHam(cavFreq, qubFreq, g, cavDim):
    cavHam, qubHam = cavQubFreeHam(cavFreq, qubFreq, cavDim)
    couplingJC = g * (sp.kron(ops.create(cavDim), ops.destroy(2), format='csc') + sp.kron(ops.destroy(cavDim), ops.create(2), format='csc'))
    JCHam = cavHam + qubHam + couplingJC
    return JCHam


def AJCHam(cavFreq, qubFreq, g, cavDim):
    cavHam, qubHam = cavQubFreeHam(cavFreq,qubFreq,cavDim)
    couplingAJC = g * (sp.kron(ops.create(cavDim), ops.create(2), format='csc') + sp.kron(ops.destroy(cavDim), ops.destroy(2), format='csc'))
    AJCHam = cavHam + qubHam + couplingAJC
    return AJCHam