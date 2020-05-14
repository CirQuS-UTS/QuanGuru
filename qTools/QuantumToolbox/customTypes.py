"""
    A module for custom types (Union etc) used in QuantumToolbox

    Types
    -----
        | **Matrix** : Type which is either spmatrix or nparray (created using TypeVar)
        | **intList** : Type for a list of integers
        | **floatList** : Type for a list of floats
        | **matrixList** : Type for a list `Matrix` types
        | **supInp** : Type from the union the types: int, `intList`, and a dict with int:float key:value combination
        | **ndOrListInt** : Type from the union of ndarray and intList
"""

from typing import Union, Dict, List, TypeVar
from numpy import ndarray # type: ignore
from scipy.sparse import spmatrix # type: ignore

# These type aliases are used in type hinting of below methods
Matrix = TypeVar('Matrix', spmatrix, ndarray)       # Type which is either spmatrix or nparray (created using TypeVar)
intList = List[int]                                 # Type for a list of integers
floatList = List[float]                             # Type for a list of floats
matrixList = List[Matrix]                           # Type for a list `Matrix` types
supInp = Union[Dict[int, float], intList, int]      # Type from the union the types: int, `intList`, and dict[int:float]
ndOrListInt = Union[ndarray, intList]              # Type from the union of ndarray and intList with integer elements
ndOrList = Union[ndarray, list]                     # Type from union of ndarray and list
