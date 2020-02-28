import scipy.sparse as sp
import scipy.sparse.linalg as slinA
import numpy as np
import scipy.linalg as linA

def Liouvillian(Hamiltonian, collapseOperators = [], decayRates = [], exp = True, timeStep = 1.0):
    sparse = sp.issparse(Hamiltonian)
    if len(collapseOperators) != 0:
        dimensionOfHilbertSpace = Hamiltonian.shape[0]
        if sparse is False:
            identity = np.identity(dimensionOfHilbertSpace)
        elif sparse is True:
            identity = sp.identity(dimensionOfHilbertSpace, format="csc")
        hamPart1 = __preSO(Hamiltonian, identity, sparse)
        hamPart2 = __posSO(Hamiltonian, identity, sparse)
        hamPart = -1j * (hamPart1 - hamPart2)
        liouvillian = hamPart
        for idx, collapseOperator in enumerate(collapseOperators):
            collapsePart = dissipator(collapseOperator, identity)
            if len(decayRates) != 0:
                liouvillian += decayRates[idx]*collapsePart
            else:
                liouvillian += collapsePart

        if exp is True:
            if sparse is True:
                liouvillianEXP = slinA.expm(liouvillian * timeStep)
            elif sparse is False:
                liouvillianEXP = linA.expm(liouvillian * timeStep)
        else:
            liouvillianEXP = liouvillian
    else:
        if sparse is True:
            liouvillianEXP = slinA.expm(-1j * Hamiltonian * timeStep)
            """h = copy.copy(Hamiltonian)
            l = linA.expm(-1j * h * timeStep)
            liouvillianEXP = sp.csc_matrix(l)"""
        else:
            liouvillianEXP = linA.expm(-1j * Hamiltonian * timeStep)
    return liouvillianEXP

def dissipator(collapseOperator, identity = []):
    sparse = sp.issparse(collapseOperator)
    if identity == []:
        dimension = collapseOperator.shape[0]
        if sparse is True:
            identity = sp.identity(dimension, format="csc")
        else:
            identity = np.identity(dimension)

    dagger = collapseOperator.conj().T

    number = dagger @ collapseOperator
    part1 = __preposSO(collapseOperator,sparse)
    part2 = __preSO(number, identity,sparse)
    part3 = __posSO(number, identity,sparse)
    return part1 - (0.5 * (part2 + part3))

def __preSO(operator, identity, sparse):
    if sparse is True:
        return sp.kron(identity, operator, format='csc')
    else:
        return np.kron(identity, operator)

def __posSO(operator, identity, sparse):
    if sparse is True:
        return sp.kron(operator.transpose(), identity, format='csc')
    else:
        return np.kron(np.transpose(operator), identity)

def __preposSO(operator,sparse):
    if sparse is True:
        return sp.kron(operator.conj(), operator, format='csc')
    else:
        return np.kron(np.conjugate(operator), operator)