import pytest
from quanguru import scqTransmon, scqTunableTransmon, QuantumToolbox
from numpy import allclose, argsort, exp, angle, abs
import pytest
from scqubits.core.descriptors import WatchedProperty
from numpy import pi, sqrt

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

    scqTransmon._resetAll()
    with pytest.warns(UserWarning, match="dimension takes precedence"):
        tmon = scqTransmon(EJ=10e9, EC=0.1e9, ng=0.0, ncut=5, dimension=21)
    assert tmon.dimension == 21
    assert tmon.ncut == 10
    assert tmon.totalHamiltonian.shape[0] == 21

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

@pytest.mark.parametrize(
    "scqClass", 
    [
        scqTransmon,
        scqTunableTransmon,
    ]
)
def test_updatingWatchedProperties(scqClass):
    """
    Test the updating of the watched properties of the scqTransmon class
        - EJ
        - EC
        - ng
    """
    scqClass._resetAll()

    watchedProperties = [attr for attr in dir(scqClass.scqType) if isinstance(getattr(scqClass.scqType, attr), WatchedProperty)]
    watchedProperties.remove('truncated_dim')

    qubit = scqClass()
    

    for prop in watchedProperties:

        qubit._paramBoundBase__paramUpdated = False

        originalValue = getattr(qubit, prop)
        if prop == 'ncut':
            newValue = originalValue + 2
        elif isinstance(originalValue, (float, int)):
            newValue = originalValue + 2
        else:
            continue

        setattr(qubit, prop, newValue)

        assert getattr(qubit, prop) == newValue
        assert getattr(qubit.scqObj, prop) == newValue
        assert qubit._paramBoundBase__paramUpdated == True

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

@pytest.mark.parametrize(
    "scqClass", 
    [
        scqTransmon,
        scqTunableTransmon,
    ]
)
def test_updateHamiltonian(scqClass):
    """
    Test that updating any of the watched properties of the scqTransmon class
    results in an updated totalHamiltonian
    """
    scqClass._resetAll()

    watchedProperties = [attr for attr in dir(scqClass.scqType) if isinstance(getattr(scqClass.scqType, attr), WatchedProperty)]
    watchedProperties.remove('truncated_dim')

    kwargs = {
        'ng': 0.25,
    }

    if 'flux' in watchedProperties:
        kwargs['flux'] = 0.1

    scqubit = scqClass(**kwargs)

    H0 = scqubit.totalHamiltonian
    
    for prop in watchedProperties:
        originalValue = getattr(scqubit, prop)
        if prop == 'ncut':
            newValue = originalValue + 2
        elif isinstance(originalValue, float):
            newValue = originalValue + pi * sqrt(2)
        elif isinstance(originalValue, int):
            newValue = originalValue + 2
        else:
            continue

        setattr(scqubit, prop, newValue)

        H1 = scqubit.totalHamiltonian

        try:
            assert not allclose(H0, H1), f"Hamiltonian did not update after changing {prop} from {originalValue} to {newValue}"
        except ValueError:
            continue

        H0 = H1

def test_find_EJ_EC():
    """
    Test the static method find_EJ_EC()
    """
    omega01 = 6.28e9 
    alpha = -223e6
    EJ, EC = scqTransmon.find_EJ_EC(omega01, alpha)
    tmon = scqTransmon(EJ=EJ, EC=EC, ng=0.0, ncut=30)
    assert allclose(tmon.E01(), omega01) and allclose(tmon.anharmonicity(), alpha)

    omega01 = 23.78
    alpha = -1.45
    EJ, EC = scqTransmon.find_EJ_EC(omega01, alpha)
    tmon = scqTransmon(EJ=EJ, EC=EC, ng=0.0, ncut=30)
    assert allclose(tmon.E01(), omega01) and allclose(tmon.anharmonicity(), alpha)

    # Invalid Inputs 

    try:
        omega01 = -1.0 
        alpha = -0.1
        scqTransmon.find_EJ_EC(omega01, alpha)
    except ValueError as e:
        assert str(e) == f'Invalid transmon properties omega01={omega01}, anharmonicity={alpha}'


    try:
        omega01 = 6.28 
        alpha = 0.1
        scqTransmon.find_EJ_EC(omega01, alpha)
    except ValueError as e:
        assert str(e) == f'Invalid transmon properties omega01={omega01}, anharmonicity={alpha}'

    try:
        omega01 = 1.0
        alpha = -2.0
        scqTransmon.find_EJ_EC(omega01, alpha)
    except ValueError as e:
        assert str(e) == f'Invalid transmon properties omega01={omega01}, anharmonicity={alpha}'
