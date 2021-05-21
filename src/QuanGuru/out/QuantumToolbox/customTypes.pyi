from numpy import ndarray
from scipy.sparse import spmatrix
from typing import Dict, List, Union

Matrix = Union[spmatrix, ndarray]
intList = List[int]
floatList = List[float]
matrixList = List[Matrix]
supInp = Union[Dict[int, float], intList, int]
ndOrListInt = Union[ndarray, intList]
ndOrList = Union[ndarray, list]
matrixOrMatrixList = Union[Matrix, matrixList]
