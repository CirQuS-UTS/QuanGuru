import scipy as np
import scipy.linalg as lina
import scipy.sparse as sp


# Functions for expectation value
def expectationMat(operator, denMat):
    expc = ((operator @ denMat).diagonal()).sum()
    return np.real(expc)


def expectationKet(operator, ket):
    denMat = ket @ (ket.conj().T)
    return expectationMat(operator, denMat)


def expectationKetList(operator, kets):
    expectations = []
    for ket in kets:
        expectations.append(expectationKet(operator, ket))
    return expectations


def expectationMatList(operator, denMats):
    expectations = []
    for denMat in denMats:
        expectations.append(expectationMat(operator, denMat))
    return expectations


def expectationColList(operator, states):
    '''
        Calculates the expectation values of a list of column
        states by matrix multiplication.
        Note: introduced to be used with eigenvectors, 
        needs to be tested for non-mutually orthogonal states
    '''
    expMat = states.conj().T @ operator @ states
    return expMat.diagonal()


# Functions for fidelity (currently only for pure states)
def fidelityKet(ket1, ket2):
    herm = ket1.conj().T
    fidelityA = ((herm @ ket2).diagonal()).sum()
    return np.real(fidelityA * np.conj(fidelityA))


def fidelityPureMat(denMat1, denMat2):
    fidelityA = ((denMat1 @ denMat2).diagonal()).sum()
    return np.real(fidelityA)


def fidelityKetLists(zippedStatesList):
    '''
    This is currently too specific
    '''
    fidelities = []
    for ind in range(len(zippedStatesList[0])):
        herm = zippedStatesList[0][ind].conj().T
        fidelityA = ((herm @ zippedStatesList[1][ind]).diagonal()).sum()
        fidelities.append(np.real(fidelityA * np.conj(fidelityA)))
    return fidelities

    
# Entropy function
def entropy(densMat, base2=False):
    # converts sparse into array (and has to)
    if not isinstance(densMat, np.ndarray):
        densMat = densMat.A

    vals = lina.eig(densMat)[0]
    nzvals = vals[vals != 0]

    if not base2:
        logvals = np.log(nzvals)
    else:
        logvals = np.log2(nzvals)

    S = float(np.real(-sum(nzvals * logvals)))
    return S


def entropyKet(ket, base2=False):
    '''
    This function should not exist at all,
    ket is always a pure state
    '''
    denMat = ket @ (ket.conj().T)
    S = entropy(denMat, base2)
    return S


def partialTrace(keep, dims, state):
    """
    Found on: https://scicomp.stackexchange.com/questions/30052/calculate-partial-trace-of-an-outer-product-in-python
    Calculate the partial trace

    ρ_a = Tr_b(ρ)

    Parameters
    ----------
    ρ : 2D array
        Matrix to trace
    keep : array
        An array of indices of the spaces to keep after
        being traced. For instance, if the space is
        A x B x C x D and we want to trace out B and D,
        keep = [0,2]
    dims : array
        An array of the dimensions of each space.
        For instance, if the space is A x B x C x D,
        dims = [dim_A, dim_B, dim_C, dim_D]

    Returns
    -------
    ρ_a : 2D array
        Traced matrix
    """
    if not isinstance(state, np.ndarray):
        state = state.toarray()

    rho = state
    if rho.shape[0] != rho.shape[1]:
        rho = (rho @ (rho.conj().T))

    keep = np.asarray(keep)
    dims = np.asarray(dims)
    Ndim = dims.size
    Nkeep = np.prod(dims[keep])

    idx1 = [i for i in range(Ndim)]
    idx2 = [Ndim+i if i in keep else i for i in range(Ndim)]
    rho_a = rho.reshape(np.tile(dims, 2))
    rho_a = np.einsum(rho_a, idx1+idx2, optimize=False)
    return rho_a.reshape(Nkeep, Nkeep)


# Delocalisation measure for various cases
def iprKet(basis, ket):
    npc = 0
    for basKet in range(len(basis)):
        fid = fidelityKet(basKet, ket)
        npc += (fid**2)
    return 1/npc


def iprKetList(basis, kets):
    npcs = []
    for ket in kets:
        npcs.append(iprKet(basis, ket))
    return npcs


def iprKetNB(ket):
    return 1/np.sum(np.power((np.abs(ket.A.flatten())),4))


def iprKetNBList(kets):
    IPRatio = []
    for ket in kets:
        IPRatio.append(iprKetNB(ket))
    return IPRatio


def iprKetNBmat(kets):
    IPRatio = []
    for ind in range(len(kets)):
        IPRatio.append(iprKetNB(kets[:,ind]))
    return IPRatio


def iprPureMat(basis, denMat):
    npc = 0
    for basKet in range(len(basis)):
        fid = fidelityPureMat(basKet, denMat)
        npc += (fid**2)
    return 1/npc


# Eigenvector statistics
def sortedEigens(totalHam):
    if not isinstance(totalHam, np.ndarray):
        totalHam = totalHam.A

    eigVals, eigVecs = lina.eig(totalHam)
    idx = eigVals.argsort()
    sortedVals = eigVals[idx]
    sortedVecs = eigVecs[:,idx]
    return sortedVals, sortedVecs


def eigVecStatKet(basis, ket):
    comps = []
    for basKet in range(len(basis)):
        comps.append(fidelityKet(basKet, ket))
    return comps


def eigVecStatKetList(basis, kets):
    compsList = []
    for ket in kets:
        compsList.append(eigVecStatKet(basis, ket))
    return compsList


def eigVecStatKetNB(ket):
    return 1/np.sum(np.power((np.abs(ket.A.flatten())),2))
