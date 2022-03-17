r"""
    Contains custom types (Union etc) used in type hints of QuantumToolbox.

    .. currentmodule:: quanguru.QuantumToolbox.customTypes

    Types
    -----

    .. autosummary::
        Matrix`
        intList`
        floatList`
        matrixList`
        supInp`
        ndOrListInt`
"""

from typing import Union, Dict, List
from numpy import ndarray # type: ignore
from scipy.sparse import spmatrix # type: ignore


# These type aliases are used in type hinting of below methods
#: Type which is either spmatrix or nparray (created using TypeVar)
Matrix = Union[spmatrix, ndarray]                   # Type which is either spmatrix or nparray (created using TypeVar) #pylint:disable=unsubscriptable-object, C0301  # noqa: E501
#Matrix = TypeVar('Matrix', spmatrix, ndarray)      # Type which is either spmatrix or nparray (created using TypeVar)

#: Type for a list of integers
intList = List[int]                                 # Type for a list of integers

#: Type for a list of floats
floatList = List[float]                             # Type for a list of floats

#: Type for a list Matrix types
matrixList = List[Matrix]                           # Type for a list Matrix types

#: Type from the union the types; int, intList, and dict[int;float]
supInp = Union[Dict[int, float], intList, int]      # Type from the union the types int, intList, and dict[int;float] #pylint:disable=unsubscriptable-object, C0301  # noqa: E501

#: Type from the union of ndarray and intList with integer elements
ndOrListInt = Union[ndarray, intList]              # Type from the union of ndarray and intList with integer elements #pylint:disable=unsubscriptable-object, C0301  # noqa: E501

#: Type from union of ndarray and list
ndOrList = Union[ndarray, list]                     # Type from union of ndarray and list #pylint:disable=unsubscriptable-object

#: Type from union of ndarray and list
matrixOrMatrixList = Union[Matrix, matrixList]      # Type from union of ndarray and list #pylint:disable=unsubscriptable-object
