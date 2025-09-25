from quanguru import QuantumSystem, number, identity, tensorProd
import numpy as np

def test_validMatrix():

    sys = QuantumSystem(dimension=2, frequency=1)
    op = np.array([[1, 0, 0], [0, 1, 0]])
    try:
        sys.operator = op
    except ValueError as ve:
        assert str(ve) == f"Matrix operator for {sys.name} must be square, but got shape (2, 3)."
    else:
        raise ValueError("ValueError was not raised for non-square matrix.")
    
    sys = QuantumSystem(frequency=1)
    op = np.array([[1]])
    try:
        sys.operator = op
    except ValueError as ve:
        assert str(ve) == f'Matrix operator for {sys.name} must have dimension > 1, but got dimension 1'
    else:
        raise ValueError("ValueError was not raised for dim=1 matrix.")

def test_singleSystemDimensionCheck():

    sys = QuantumSystem(dimension=3, frequency=1)
    op = np.array([[1, 0], [0, 1]])
    try:
        sys.operator = op
    except ValueError as ve:
        assert str(ve) == f'Matrix operator dimension (2) does not match quantum system {sys.name} dimension (3)'
    else:
        raise ValueError("ValueError was not raised for dimension mismatch.")

def test_singleSystemDimensionUpdate():

    sys = QuantumSystem(frequency=1)
    op = np.array([[1, 0], [0, 1]])
    sys.operator = op
    
    assert sys.dimension == 2
    assert np.array_equal(sys.operator, op)

def test_singleSystemDimensionSet():

    sys = QuantumSystem(frequency=1)
    op = np.array([[1, 0], [0, 1]])
    sys.operator = op

    try:
        sys.dimension = 3
    except ValueError as ve:
        assert str(ve) == f'Cannot change dimension of {sys.name} from 2 to 3 because it has terms with matrix operators. Matrix operators have fixed dimensions.'
    else:
        raise ValueError("ValueError was not raised for dimension mismatch.")

def test_multitermDimensionCheck():

    sys = QuantumSystem(dimension=5, frequency=1)
    op1 = number
    op2 = np.array([[0, 1], [1, 0]])
    term1 = sys.createTerm(operator=op1)
    try:
        term2 = sys.createTerm(operator=op2)
    except ValueError as ve:
        assert str(ve) == f'Matrix operator dimension (2) does not match quantum system {sys.name} dimension (5)'
    else:
        raise ValueError("ValueError was not raised for dimension mismatch.")

def test_multitermDimensionUpdate():
    
    sys = QuantumSystem(frequency=1)
    op1 = number
    op2 = np.array([[0, 1], [1, 0]])
    term1 = sys.createTerm(operator=op1)
    term2 = sys.createTerm(operator=op2)

    assert sys.dimension == 2
    assert np.isclose(sys.totalHamiltonian, op1(2) + op2)

def test_multitermDimensionSet():

    sys = QuantumSystem(dimension=2, frequency=1)
    op1 = np.array([[1, 0], [0, 1]])
    op2 = np.array([[0, 1], [1, 0]])
    term1 = sys.createTerm(operator=op1)
    term2 = sys.createTerm(operator=op2)

    assert np.isclose(sys.totalHamiltonian, op1 + op2)
    try:
        sys.dimension = 3
    except ValueError as ve:
        assert str(ve) == f'Cannot change dimension of {sys.name} from 2 to 3 because it has terms with matrix operators. Matrix operators have fixed dimensions.'
    else:
        raise ValueError("ValueError was not raised for dimension mismatch.")

def test_couplingTermDimensionCheck():

    sys1 = QuantumSystem(dimension=2, frequency=1)
    sys2 = QuantumSystem(dimension=3, frequency=1)
    sys = sys1 + sys2
    op1 = np.array([[1, 0], [0, 1]])
    op2 = np.array([[1, 1], [1, 1]])
    try:
        qterm = sys.createTerm(qSystem=[sys1, sys2], operator=[op1, op2])
    except ValueError as ve:
        assert str(ve) == f'Matrix operator dimension (2) does not match quantum system {sys2.name} dimension (3)'
    else:
        raise ValueError("ValueError was not raised for dimension mismatch.")
    
def test_couplingTermDimensionUpdate():

    sys1 = QuantumSystem(frequency=1, operator=number)
    sys2 = QuantumSystem(frequency=1, operator=number)
    sys = sys1 + sys2
    op1 = np.array([[1, 0], [0, 1]])
    op2 = np.array([[0, 1], [1, 0]])
    qterm = sys.createTerm(qSystem=[sys1, sys2], operator=[op1, op2], frequency=1)

    assert sys.dimension == 4
    assert np.array_equal(sys.totalHamiltonian.toarray(), tensorProd(op1, op2) + tensorProd(number(2), identity(2)).toarray() + tensorProd(identity(2), number(2)).toarray())

def test_couplingTermDimensionSet():

    sys1 = QuantumSystem(dimension=2, frequency=1, operator=number)
    sys2 = QuantumSystem(dimension=2, frequency=1, operator=number)
    sys = sys1 + sys2
    op1 = np.array([[1, 0], [0, 1]])
    op2 = np.array([[0, 1], [1, 0]])
    qterm = sys.createTerm(qSystem=[sys1, sys2], operator=[op1, op2], frequency=1)

    assert np.array_equal(sys.totalHamiltonian.toarray(), tensorProd(op1, op2) + tensorProd(number(2), identity(2)).toarray() + tensorProd(identity(2), number(2)).toarray())
    try:
        sys2.dimension = 3
    except ValueError as ve:
        assert str(ve) == f'Cannot change dimension of {sys2.name} from 2 to 3 because it has terms with matrix operators. Matrix operators have fixed dimensions.'
    else:
        raise ValueError("ValueError was not raised for dimension mismatch.")

# test that setting the operator as a matrix works for single terms and coupling terms
# test that setting the operator as a matrix correctly checks the dimension

# composite systems