r"""
    QuantumToolbox consists **purely of Python functions** (no other objects) that create and/or use **matrices**.
    **Bold** parts of the previous sentence highlight two main ideas of QuantumToolbox.

    It only contains Python functions to make it familiar with a broader audience, so that anyone without any interest
    in object-oriented programming can still contribute to QuantumToolbox, and the second idea is to use scipy sparse
    (csc matrix) as default.
    Matrix creations should be sparse as default and return .A (or .toarray()) of the created sparse if sparse=False.
    Any function manipulating matrices should be designed to be independent of sparse or array, if possible.

    .. currentmodule:: quanguru.QuantumToolbox

    Modules
    -------

    .. autosummary::
        linearAlgebra

    .. autosummary::
        states
        operators
        evolution

    .. autosummary::
        functions
        Hamiltonians
        spinRotations
        basicGates
        quasiProbabilities

    .. autosummary::
        eigenVecVal
        rmtDistributions
        IPR
        thermodynamics
        _helpers
        customTypes

"""

from .customTypes import (Matrix, intList, matrixList, supInp, ndOrListInt, ndOrList)
from .linearAlgebra import (hc, innerProd, norm, outerProd, tensorProd, trace, partialTrace, _matMulInputs, _matPower)
from .states import (
    basis, completeBasis, basisBra, zerosKet, zerosMat, weightedSum, superPos, densityMatrix, completeBasisMat,
    normalise, compositeState, mat2Vec, vec2Mat, BellStates, purity
)
from .operators import (
    number, destroy, create, identity, sigmaz, sigmay, sigmax, sigmap, sigmam, Jz, Jp, Jm, Jx, Jy, Js, operatorPow,
    paritySUM, parityEXP, displacement, squeeze, compositeOp
)
from .evolution import (
    Unitary, Liouvillian, LiouvillianExp, dissipator, _preSO, _postSO, _prepostSO, evolveOpen, steadyState
)
from .functions import (
    expectation, fidelityPure, entropy, sortedEigens, concurrence, traceDistance, _expectationColArr,
    standardDev, spectralNorm, _fidelityTest
)
from ._helpers import (loopIt)
from .rmtDistributions import (EigenVectorDist, WignerDyson, WignerSurmise, Poissonian)
from .thermodynamics import(nBarThermal, qubitPolarisation, HeatCurrent)
from .spinRotations import(qubRotation, xRotation, yRotation, zRotation)
from .quasiProbabilities import (Wigner, HusimiQ, _qfuncPure)
from .Hamiltonians import (qubCavFreeHam, RabiHam, JCHam, aJCHam, UJC)
from .IPR import (iprKet, iprKetNB)
from .eigenVecVal import (_eigs, _eigStat, _eigStatSymp, _eigStatEig, eigVecStatKet)
from .basicGates import (CNOT, CPHASE, Hadamard)
