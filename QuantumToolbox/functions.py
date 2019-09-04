import scipy as np
import scipy.linalg as lina
from QuantumToolbox.states import densityMatrix


def expectationSparse(operator, state, ket=True):
    if ket:
        expc = np.array(((state.getH()) @ operator @ state).diagonal()).sum()
    else:
        expc = np.array((operator @ state).diagonal()).sum()
    return np.real(expc)


def fidelitySparse(state1, state2, ket=True):
    """
    Fidelity between two PURE states
    :param state1: ket or density matrix of PURE state1
    :param state2: ket or density matrix of PURE state1
    :param ket: are given PURE states ket (True) or density matrix (False)
    :return: overlap fidelity
    """

    if ket:
        fidelityA = np.array(((state1.getH()) @ state2).diagonal()).sum()
    else:
        fidelityA = np.array((state1 @ state2).diagonal()).sum()

    return np.sqrt(np.real(fidelityA * np.conj(fidelityA))) if ket else np.sqrt(np.real(fidelityA))


def entropy(psi, ket = True, base2 = False):
    if ket:
        densMat = densityMatrix(psi)
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


def partial_trace(rho, keep, dims, optimize=False):
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
    if not isinstance(rho, np.ndarray):
        rho = rho.toarray()

    if rho.shape[0] != rho.shape[1]:
        rho = densityMatrix(rho)

    keep = np.asarray(keep)
    dims = np.asarray(dims)
    Ndim = dims.size
    Nkeep = np.prod(dims[keep])

    idx1 = [i for i in range(Ndim)]
    idx2 = [Ndim+i if i in keep else i for i in range(Ndim)]
    rho_a = rho.reshape(np.tile(dims,2))
    rho_a = np.einsum(rho_a, idx1+idx2, optimize=optimize)
    return rho_a.reshape(Nkeep, Nkeep)