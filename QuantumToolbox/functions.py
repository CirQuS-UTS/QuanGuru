import scipy as np
import scipy.linalg as lina
import QuantumToolbox.states as states


def expectationKet(operator, state):
    expc = (((state.conj().T) @ operator @ state).diagonal()).sum()
    return np.real(expc)


def expectationMat(operator, state):
    expc = ((operator @ state).diagonal()).sum()
    return np.real(expc)


def expectationList(operator, states):
    expectations = []
    if states[0].shape[0] != states[0].shape[1]:
        for state in states:
            expectations.append(np.real((((state.getH()) @ operator @ state).diagonal()).sum()))
    else:
        for state in states:
            expectations.append(np.real(((operator @ state).diagonal()).sum()))
    return expectations


def expectationCollList(operator, states):
    '''
        Calculates the expectation values of a list of collumn
        states thru matrix multiplication
    '''
    expMat = states.conj().T @ operator @ states
    return expMat.diagonal()


def fidelityKet(state1, state2):
    herm = state1.conj().T
    fidelityA = ((herm @ state2).diagonal()).sum()
    return np.real(fidelityA * np.conj(fidelityA))


def fidelityPureMat(state1, state2):
    fidelityA = ((state1 @ state2).diagonal()).sum()
    return np.real(fidelityA)


def entropy(psi, base2=False):
    if psi.shape[0] != psi.shape[1]:
        densMat = states.densityMatrix(psi)
    else:
        densMat = psi

    if not isinstance(densMat, np.ndarray):
        densMat = densMat.toarray()

    vals = lina.eig(densMat)[0]
    nzvals = vals[vals != 0]

    if not base2:
        logvals = np.log(nzvals)
    else:
        logvals = np.log2(nzvals)

    S = float(np.real(-sum(nzvals * logvals)))
    return S


def partial_trace(keep, dims, rho):
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
    if rho.shape[0] != rho.shape[1]:
        rho = states.densityMatrix(rho)

    if not isinstance(rho, np.ndarray):
        rho = rho.toarray()

    keep = np.asarray(keep)
    dims = np.asarray(dims)
    Ndim = dims.size
    Nkeep = np.prod(dims[keep])

    idx1 = [i for i in range(Ndim)]
    idx2 = [Ndim+i if i in keep else i for i in range(Ndim)]
    rho_a = rho.reshape(np.tile(dims, 2))
    rho_a = np.einsum(rho_a, idx1+idx2, optimize=False)
    return rho_a.reshape(Nkeep, Nkeep)


def IPRket(basis, state):
    """
    :param basis: A generic BRA basis
    :param state: in ket
    :return: IPR
    """
    npc = 0
    for khyu in range(len(basis)):
        fidelityA = ((basis[khyu] @ state).diagonal()).sum()
        fid = np.real(fidelityA * np.conj(fidelityA))
        npc += (fid**2)
    return 1/npc
