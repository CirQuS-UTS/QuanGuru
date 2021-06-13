from .customTypes import Matrix as Matrix
from .operators import create as create, destroy as destroy, identity as identity, number as number, sigmam as sigmam, sigmap as sigmap, sigmax as sigmax, sigmaz as sigmaz
from typing import Tuple

def qubCavFreeHam(qubFreq: float, cavFreq: float, cavDim: int) -> Tuple[Matrix, Matrix]: ...
def RabiHam(qubFreq: float, cavFreq: float, g: float, cavDim: int) -> Matrix: ...
def JCHam(qubFreq: float, cavFreq: float, g: float, cavDim: int) -> Matrix: ...
def aJCHam(qubFreq: float, cavFreq: float, g: float, cavDim: int) -> Matrix: ...