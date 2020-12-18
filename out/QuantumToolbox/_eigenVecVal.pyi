from .customTypes import Matrix as Matrix, floatList as floatList, matrixList as matrixList
from .functions import fidelityPure as fidelityPure

def eigVecStatKet(basis: matrixList, ket: Matrix) -> floatList: ...
