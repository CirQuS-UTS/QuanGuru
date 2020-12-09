import random as rn
import numpy as np
import scipy.sparse as sp
import pytest
from qTools.QuantumToolbox import linearAlgebra as la #pylint: disable=import-error

oper = np.array(
    [
        [rn.random() + rn.random()*1j, rn.random() - rn.random()*1j, rn.random() + rn.random()*1j, rn.random()*1j],
        [rn.random(), rn.random(), rn.random(), rn.random()],
        [-rn.random()*1j, rn.random()*1j, -rn.random()*1j, rn.random()*1j],
        [rn.random(), rn.random()*1j, rn.random()-rn.random()*1j, rn.random()-rn.random()*1j]
    ])

operEx1 = np.array(
    [
        [1+1j, 2+2j],
        [3+3j, 4+4j]
    ])

operEx2 = np.array(
    [
        [0, 1],
        [1, 0]
    ])

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

cmind1 = [1, 0]
cmind2 = [0, 1]
cmind3 = [3/5, 4j/5]
cmind4 = [1, 1j]
inps1 = [rn.random()+rn.random()*1j for i in range(5)]
inps2 = [rn.random()+rn.random()*1j for i in range(5)]

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
    assert round(la.innerProd(columnMat) - sum([i * np.conj(i) for i in elements]), 14) == 0+0j

@pytest.mark.parametrize("columnMats, elements", forOthers)
def test_innerProductWithOther(columnMats, elements):
    # Calculate the inner product and compare the output with explicit definition (difference need to be zero)
    dif = la.innerProd(columnMats[0], columnMats[1]) - sum([i * np.conj(j) for (i, j) in zip(elements[0], elements[1])])
    assert round(dif, 14) == 0+0j

@pytest.mark.parametrize("columnMat, elements", forSelf)
def test_outerProductWithItself(columnMat, elements):
    # Calculate the outer product and compare the output with explicit definition (difference need to be zero)
    outProd = la.outerProd(columnMat)
    dim = columnMat.shape[0]
    for ind1 in range(dim):
        for ind2 in range(dim):
            dif = outProd[ind1][ind2] - elements[ind1] * np.conj(elements[ind2])
            assert round(dif, 14) == 0+0j

@pytest.mark.parametrize("columnMats, elements", forOthers)
def test_outerProductWithOther(columnMats, elements):
    # Calculate the outer product and compare the output with explicit definition (difference need to be zero)
    outProd = la.outerProd(columnMats[0], columnMats[1])
    dim = columnMats[0].shape[0]
    for ind1 in range(dim):
        for ind2 in range(dim):
            dif = outProd[ind1][ind2] - elements[0][ind1] * np.conj(elements[1][ind2])
            assert round(dif, 14) == 0+0j

@pytest.mark.parametrize("mats", [[cMatEx1, cMatEx2], [cMatEx1, cMatEx3], [cMatEx1, cMatEx4], [cMatEx2, cMatEx3],
                                  [cMatEx1, cMatEx2, cMatEx3], [cMatEx1, cMatEx4, cMatEx3], [cMatEx2, cMatEx4, cMatEx3],
                                  [cMatEx1, cMatEx4, cMatEx3, cMatEx2], [cMat1, cMat2, cMat1], [cMat1, cMat2],
                                  [oper, 4, oper], [operEx1, 3, operEx2], [operEx3, operEx1, operEx2]])
def test_tensorProduct(mats):
    # the functions is recursive, here it is tested by doing the same thing in a for loop
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
    # trace is too simple to test, this one calculates a tensor product and takes partial trace and compare with the
    # given matrices (inputs are columns matrices, so first creates square matrices using outerProd)
    dims = [mat.shape[0] for mat in mats]
    mats = [la.outerProd(mat) for mat in mats]
    tensProd = la.tensorProd(*mats)
    for i in range(len(dims)):
        pti = la.partialTrace([i], dims, tensProd)
        assert np.allclose(pti, mats[i])
