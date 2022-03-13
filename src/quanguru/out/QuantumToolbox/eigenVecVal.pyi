from .customTypes import Matrix as Matrix, floatList as floatList, matrixList as matrixList
from .functions import fidelityPure as fidelityPure
from .states import mat2Vec as mat2Vec
from typing import Tuple

def eigVecStatKet(basis: matrixList, ket: Matrix, symp: bool = ...) -> Tuple: ...
