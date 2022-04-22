import random as rn
import numpy as np
import scipy.sparse as sp
import pytest
from quanguru.QuantumToolbox import linearAlgebra as la #pylint: disable=import-error
import quanguru.QuantumToolbox.operators as qOps

# a random 4 x 4 (complex-valued) matrix to be used is testing linearAlgebra functions
oper = np.array(
    [
        [rn.random() + rn.random()*1j, rn.random() - rn.random()*1j, rn.random() + rn.random()*1j, rn.random()*1j],
        [rn.random(), rn.random(), rn.random(), rn.random()],
        [-rn.random()*1j, rn.random()*1j, -rn.random()*1j, rn.random()*1j],
        [rn.random(), rn.random()*1j, rn.random()-rn.random()*1j, rn.random()-rn.random()*1j]
    ])

# a (hard-coded) 2 x 2 (complex-valued) matrix to be used is testing linearAlgebra functions
operEx1 = np.array(
    [
        [1+1j, 2+2j],
        [3+3j, 4+4j]
    ])

# a (hard-coded) 2 x 2 (real-valued) matrix to be used is testing linearAlgebra functions
operEx2 = np.array(
    [
        [0, 1],
        [1, 0]
    ])

# a (hard-coded) 2 x 2 (complex-valued) matrix to be used is testing linearAlgebra functions
operEx3 = np.array(
    [
        [1, 0, 0],
        [0, 1, 0],
        [1j, 0, 1]
    ])

@pytest.mark.parametrize("op", [oper, operEx1, operEx2, operEx3])
def test_hermitianCongujation(op):
    # Calculate the hermitian conjugate and assert that the real (imaginary) parts of the cross-diagonal elements are
    # the same (negative of the other)
    operHC = la.hc(op)
    dim = op.shape[0]
    for ind1 in range(dim):
        for ind2 in range(dim):
            n = op[ind1][ind2]
            nc = operHC[ind2][ind1]
            assert (n.real-nc.real) == 0
            assert (n.imag+nc.imag) == 0

# list of elements in below column matrices to be used is testing linearAlgebra functions
cmind1 = [1, 0]
cmind2 = [0, 1]
cmind3 = [3/5, 4j/5]
cmind4 = [1, 1j]
inps1 = [rn.random()+rn.random()*1j for i in range(5)]
inps2 = [rn.random()+rn.random()*1j for i in range(5)]

# some column matrices to be used is testing linearAlgebra functions
cMatEx1 = np.array(
    [
        [1],
        [0]
    ])

cMatEx2 = np.array(
    [
        [0],
        [1]
    ])

cMatEx3 = (1/5)*np.array(
    [
        [3],
        [4j]
    ])

cMatEx4 = np.array(
    [
        [1],
        [1j]
    ])

cMat1 = np.array(
    [
        [inps1[0]],
        [inps1[1]],
        [inps1[2]],
        [inps1[3]],
        [inps1[4]]
    ])

cMat2 = np.array(
    [
        [inps2[0]],
        [inps2[1]],
        [inps2[2]],
        [inps2[3]],
        [inps2[4]]
    ])

# some bundling of column matrices and their corresponding entry lists to be used is testing linearAlgebra functions
forSelf = [(cMatEx1, cmind1), (cMatEx2, cmind2), (cMatEx3, cmind3), (cMatEx4, cmind4), (cMat1, inps1), (cMat2, inps2)]
forOthers = [([cMatEx1, cMatEx2], [cmind1, cmind2]), ([cMatEx1, cMatEx3], [cmind1, cmind3]),
             ([cMatEx1, cMatEx4], [cmind1, cmind4]), ([cMatEx2, cMatEx1], [cmind2, cmind1]), 
             ([cMatEx2, cMatEx3], [cmind2, cmind3]), ([cMatEx2, cMatEx4], [cmind2, cmind4]),
             ([cMatEx3, cMatEx1], [cmind3, cmind1]), ([cMatEx3, cMatEx2], [cmind3, cmind2]),
             ([cMatEx3, cMatEx4], [cmind3, cmind4]), ([cMatEx4, cMatEx1], [cmind4, cmind1]),
             ([cMatEx4, cMatEx2], [cmind4, cmind2]), ([cMatEx4, cMatEx3], [cmind4, cmind3]),
             ([cMat1, cMat2], [inps1, inps2]), ([cMat2, cMat1], [inps2, inps1])]

@pytest.mark.parametrize("columnMat, elements", forSelf)
def test_innerProductWithItself(columnMat, elements):
    # Calculate the inner product and compare the output with explicit definition (difference need to be zero)
    assert np.round(la.innerProd(columnMat) - sum([i * np.conj(i) for i in elements]), 14) == 0+0j

@pytest.mark.parametrize("columnMats, elements", forOthers)
def test_innerProductWithOther(columnMats, elements):
    # Calculate the inner product and compare the output with explicit definition (difference need to be zero)
    dif = la.innerProd(columnMats[0], columnMats[1]) - sum([i * np.conj(j) for (i, j) in zip(elements[0], elements[1])])
    assert np.round(dif, 14) == 0+0j

@pytest.mark.parametrize("columnMat, elements", forSelf)
def test_outerProductWithItself(columnMat, elements):
    # Calculate the outer product and compare the output with explicit definition (difference need to be zero)
    outProd = la.outerProd(columnMat)
    dim = columnMat.shape[0]
    for ind1 in range(dim):
        for ind2 in range(dim):
            dif = outProd[ind1][ind2] - elements[ind1] * np.conj(elements[ind2])
            assert np.round(dif, 14) == 0+0j

@pytest.mark.parametrize("columnMats, elements", forOthers)
def test_outerProductWithOther(columnMats, elements):
    # Calculate the outer product and compare the output with explicit definition (difference need to be zero)
    outProd = la.outerProd(columnMats[0], columnMats[1])
    dim = columnMats[0].shape[0]
    for ind1 in range(dim):
        for ind2 in range(dim):
            dif = outProd[ind1][ind2] - elements[0][ind1] * np.conj(elements[1][ind2])
            assert np.round(dif, 14) == 0+0j

@pytest.mark.parametrize("mats", [[cMatEx1, cMatEx2], [cMatEx1, cMatEx3], [cMatEx1, cMatEx4], [cMatEx2, cMatEx3],
                                  [cMatEx1, cMatEx2, cMatEx3], [cMatEx1, cMatEx4, cMatEx3], [cMatEx2, cMatEx4, cMatEx3],
                                  [cMatEx1, cMatEx4, cMatEx3, cMatEx2], [cMat1, cMat2, cMat1], [cMat1, cMat2],
                                  [oper, 4, oper], [operEx1, 3, operEx2], [operEx3, operEx1, operEx2]])
def test_tensorProduct(mats):
    # the function is recursive, here it is tested by doing the same thing in a for loop
    tenProd = la.tensorProd(*mats).A
    totalProd = 1
    for arg in mats:
        if isinstance(arg, int):
            arg = sp.identity(arg, format="csc")
        totalProd = sp.kron(totalProd, arg, format='csc')
    dif = tenProd - totalProd.A
    assert np.allclose(dif, np.zeros(shape=tenProd.shape))

@pytest.mark.parametrize("mats", [[cMatEx1, cMatEx1, cMatEx1, cMatEx1], [cMatEx1, cMatEx2, cMatEx1, cMatEx2],
                                  [cMatEx3, cMatEx1, cMatEx2, cMatEx1], [cMatEx2, cMatEx3, cMatEx2, cMatEx3],
                                  [cMatEx1, cMatEx3, cMatEx2, cMatEx2], [cMatEx3, cMatEx3, cMatEx2, cMatEx2]])
def test_partialTrace(mats):
    # calculates a tensor product and takes partial trace and compares with the
    # given matrices (inputs are columns matrices, so first creates square matrices using outerProd)
    dims = [mat.shape[0] for mat in mats]
    mats = [la.outerProd(mat) for mat in mats]
    tensProd = la.tensorProd(*mats)
    for i in range(len(dims)):
        pti = la.partialTrace([i], dims, tensProd)
        assert np.allclose(pti, mats[i])

@pytest.mark.parametrize("mat, n", [[cMatEx1, 1], [cMatEx2, 1], [cMatEx3, 1], [cMatEx4, np.sqrt(2)]])
def test_norm(mat, n):
    # calculate the norm and compare it with the expected results
    assert la.norm(mat) == n

@pytest.mark.parametrize("mat, t", [[operEx1, 5+5j], [operEx2, 0], [operEx3, 3]])
def test_trace(mat, t):
    # calculate the trace and compare it with the expected results
    assert la.trace(mat) == t

@pytest.mark.parametrize("sp", [False, True])
def test_matrixPowerRaising(sp):
    oper1 = qOps.sigmax(sparse=sp)
    oper2 = qOps.number(5, sparse=sp)
    oper3 = qOps.destroy(8, sparse=sp)

    if sp:
        assert np.allclose(la._matPower(oper1, 1).A, oper1.A)
        assert np.allclose(la._matPower(oper2, 1).A, oper2.A)
        assert np.allclose(la._matPower(oper3, 1).A, oper3.A)
    else:
        assert np.allclose(la._matPower(oper1, 1), oper1)
        assert np.allclose(la._matPower(oper2, 1), oper2)
        assert np.allclose(la._matPower(oper3, 1), oper3)

    if sp:
        assert np.allclose(la._matPower(oper1, 2).A, (oper1@oper1).A)
        assert np.allclose(la._matPower(oper2, 2).A, (oper2@oper2).A)
        assert np.allclose(la._matPower(oper3, 2).A, (oper3@oper3).A)
    else:
        assert np.allclose(la._matPower(oper1, 2), (oper1@oper1))
        assert np.allclose(la._matPower(oper2, 2), (oper2@oper2))
        assert np.allclose(la._matPower(oper3, 2), (oper3@oper3))

    if sp:
        assert np.allclose(la._matPower(oper1, 3).A, (oper1@oper1@oper1).A)
        assert np.allclose(la._matPower(oper2, 3).A, (oper2@oper2@oper2).A)
        assert np.allclose(la._matPower(oper3, 3).A, (oper3@oper3@oper3).A)
    else:
        assert np.allclose(la._matPower(oper1, 3), (oper1@oper1@oper1))
        assert np.allclose(la._matPower(oper2, 3), (oper2@oper2@oper2))
        assert np.allclose(la._matPower(oper3, 3), (oper3@oper3@oper3))
