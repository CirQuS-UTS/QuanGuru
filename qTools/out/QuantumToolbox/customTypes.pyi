from numpy import ndarray
from scipy.sparse import spmatrix
from typing import Dict, List, TypeVar, Union

Matrix = TypeVar('Matrix', spmatrix, ndarray)
intList = List[int]
floatList = List[float]
matrixList = List[Matrix]
supInp = Union[Dict[int, float], intList, int]
ndOrList_int = Union[ndarray, intList]
ndOrList = Union[ndarray, list]
