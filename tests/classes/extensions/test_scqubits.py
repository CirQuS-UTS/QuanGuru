from quanguru import scqTransmon, QuantumToolbox
from numpy import allclose, argsort, exp, angle, abs

def test_scqTransmonDimension():
    """
    Test the getting and setting of the dimension attribute of the scqTransmon class
        - on instantiation
        - after instantiation
        - using ncut attribute
        - using scqubit.ncut attribute
        - the size of totalHamiltonian matches the dimension
    """

    tmon = scqTransmon(dimension=21, EJ=20e9, EC=0.2e9, ng=0.0)
    assert tmon.dimension == 21
    assert tmon.ncut == 10
    assert tmon.totalHamiltonian.shape[0] == 21

    tmon.dimension = 31
    assert tmon.dimension == 31
    assert tmon.ncut == 15
    assert tmon.totalHamiltonian.shape[0] == 31

    tmon.ncut = 20
    assert tmon.dimension == 41
    assert tmon.ncut == 20
    assert tmon.totalHamiltonian.shape[0] == 41

    tmon.scqObj.ncut = 25
    assert tmon.dimension == 51
    assert tmon.ncut == 25
    assert tmon.totalHamiltonian.shape[0] == 51

    scqTransmon._resetAll()

    tmon = scqTransmon(EJ=10e9, EC=0.1e9, ng=0.0, ncut=5)
    assert tmon.dimension == 11
    assert tmon.ncut == 5
    assert tmon.totalHamiltonian.shape[0] == 11

def test_invalidDimension():
    """
    Test the setting of invalid dimension values for the scqTransmon class
        - even numbers
        - non-integer values
    """

    try:
        tmon = scqTransmon(dimension=20, EJ=20e9, EC=0.2e9, ng=0.0)
    except ValueError as e:
        assert str(e) == 'dimension must be odd for scqubits qubits'

    tmon = scqTransmon(dimension=21, EJ=20e9, EC=0.2e9, ng=0.0)

    try:
        tmon.dimension = 30
    except ValueError as e:
        assert str(e) == 'dimension must be odd for scqubits qubits'

    try:
        tmon.dimension = 21.5
    except ValueError as e:
        assert str(e) == 'dimension must be an integer'

def test_updatingWatchedProperties():
    """
    Test the updating of the watched properties of the scqTransmon class
        - EJ
        - EC
        - ng
    """

    tmon = scqTransmon(dimension=21, EJ=20e9, EC=0.2e9, ng=0.0)
    assert tmon.EJ == 20e9
    assert tmon.EC == 0.2e9
    assert tmon.ng == 0.0

    tmon._paramBoundBase__paramUpdated = False

    tmon.scqObj.EJ = 25e9
    assert tmon.EJ == 25e9
    assert tmon.scqObj.EJ == 25e9
    assert tmon._paramBoundBase__paramUpdated == True

    tmon._paramBoundBase__paramUpdated = False

    tmon.scqObj.EC = 0.25e9
    assert tmon.EC == 0.25e9
    assert tmon.scqObj.EC == 0.25e9
    assert tmon._paramBoundBase__paramUpdated == True

    tmon._paramBoundBase__paramUpdated = False

    tmon.scqObj.ng = 0.1
    assert tmon.ng == 0.1
    assert tmon.scqObj.ng == 0.1
    assert tmon._paramBoundBase__paramUpdated == True

# def test_getAttribute():
#     """
#     Test the __getattribute__ method of the scqTransmon class
#         - getting attributes from the scqTransmon class
#         - getting attributes from the QuantumSystem class
#         - getting attributes from the scqubit.Transmon class
#     """
#     tmon = scqTransmon(dimension=21, EJ=20e9, EC=0.2e9, ng=0.0)

#     assert tmon.ncut == 10
#     assert tmon.EJ == 20e9
#     assert tmon.EC == 0.2e9
#     assert tmon.ng == 0.0

def test_eigenstate():
    """
    Test the eigenstate method of the scqTransmon class
        - returns the correct number of eigenstates
        - returns the correct eigenstate for a given index
    """

    tmon = scqTransmon(dimension=21, EJ=20e9, EC=0.2e9, ng=0.0)

    state = tmon.eigenstate(n=0)
    assert state.shape == (21, 1)

    vals, vecs = QuantumToolbox._eigs(tmon.totalHamiltonian)

    indices = argsort(vals)
    vecs = vecs[:, indices]

    for i in range(min(5, tmon.dimension)):
        state = tmon.eigenstate(n=i)
        comp = vecs[:, [i]]

        if state[0, 0] < 0:
            state = -state
        if comp[0, 0] < 0:
            comp = -comp

        assert allclose(state, comp)

