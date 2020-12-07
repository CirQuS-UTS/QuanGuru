"""
    QuantumToolbox consists **purely of Python functions** (no other objects) that create and/or use **matrices**.
    The **bold** parts of the previous sentence highlights two main design ideas of QuantumToolbox.

    It only contains Python functions to make it familiar with a broader audience, so that anyone without any interest
    in object-oriented programming can still contribute to QuantumToolbox. While doing so, it is better to follow the
    second idea that is using spicy sparse (csc matrix) as default.

    Matrix creations should be sparse as default and return .A (or .toarray()) of the created sparse if sparse=False.
    Any function manipulating matrices should be designed to be independent of sparse or array, if possible.

    .. autosummary::
        :toctree: stubs

        states
        operators
        evolution
        functions
        Hamiltonians
        quasiProbabilities
        rmtDistributions

"""

from .customTypes import (Matrix, intList, matrixList, supInp, ndOrListInt, ndOrList)
from .linearAlgebra import (hc, innerProd, norm, outerProd, tensorProd, trace, partialTrace)
from .states import (
    basis, completeBasis, basisBra, zeros, weightedSum, superPos, densityMatrix, completeBasisMat, normalise,
    compositeState, mat2Vec, vec2Mat
)
from .operators import (
    number, destroy, create, identity, sigmaz, sigmay, sigmax, sigmap, sigmam, Jz, Jp, Jm, Jx, Jy, Js, operatorPow,
    paritySUM, parityEXP, displacement, squeeze, compositeOp
)
from .functions import (expectation, fidelity, entropy, sortedEigens, concurrence)






from .Hamiltonians import (cavQubFreeHam, RabiHam, JCHam, aJCHam)
from .evolution import (Unitary, Liouvillian, LiouvillianExp, dissipator, _preSO, _posSO, _preposSO)

from .quasiProbabilities import (Wigner, HusimiQ, _qfuncPure)



from .rmtDistributions import (EigenVectorDist, WignerDyson, Poissonian)
from ._undecided import (expectationKetList, expectationMatList, expectationColArr, fidelityKetList, fidelityKetLists)
from ._IPR import (iprKet, iprKetList, iprKetNB, iprKetNBList, iprKetNBmat, iprPureDenMat)
from ._eigenVecVal import (_eigStat, _eigStatSymp, eigVecStatKet, eigVecStatKetList, eigVecStatKetNB)
