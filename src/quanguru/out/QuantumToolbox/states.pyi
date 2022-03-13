from .customTypes import Matrix as Matrix, intList as intList, matrixList as matrixList, matrixOrMatrixList as matrixOrMatrixList, supInp as supInp
from typing import Any, Iterable, List, Optional

def basis(dimension: int, state: int, sparse: bool = ...) -> Matrix: ...
def completeBasis(dimension: int, sparse: bool = ...) -> matrixList: ...
def basisBra(dimension: int, state: int, sparse: bool = ...) -> Matrix: ...
def zerosKet(dimension: int, sparse: bool = ...) -> Matrix: ...
def zerosMat(dimension: int, sparse: bool = ...) -> Matrix: ...
def weightedSum(summands: Iterable, weights: Iterable = ...) -> Any: ...
def superPos(dimension: int, excitations: supInp, populations: bool = ..., sparse: bool = ...) -> Matrix: ...
def densityMatrix(ket: matrixOrMatrixList, probability: Iterable[Any] = ...) -> Matrix: ...
def completeBasisMat(dimension: Optional[int] = ..., compKetBase: Optional[matrixList] = ..., sparse: bool = ...) -> matrixList: ...
def normalise(state: Matrix) -> Matrix: ...
def compositeState(dimensions: intList, excitations: List[supInp], sparse: bool = ...) -> Matrix: ...
def mat2Vec(denMat: Matrix) -> Matrix: ...
def vec2Mat(vec: Matrix) -> Matrix: ...
def BellStates(bs: str = ..., sparse: bool = ...) -> Matrix: ...
def purity(denMat: Matrix) -> float: ...
