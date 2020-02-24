import scipy.sparse as sp
import scipy.linalg as linA
import numpy as np

def compositeOp(operator, dimB, dimA):
    if (dimB <= 1) and (dimA > 1):
        return sp.kron(operator,sp.identity(dimA), format='csc')
    elif (dimB > 1) and (dimA <= 1):
        return sp.kron(sp.identity(dimB), operator, format='csc')
    elif (dimB > 1) and (dimA > 1):
        return sp.kron(sp.kron(sp.identity(dimB), operator, format='csc'), sp.identity(dimA), format='csc')
    else:
        return operator

def number(N, sparse=True):
    data = [i for i in range(N)]
    rows = range(0, N)
    columns = range(0, N)
    n = sp.csc_matrix((data, (rows, columns)), shape=(N, N))
    return n if sparse == True else n.toarray()

def destroy(N, sparse=True):
    data = [np.sqrt(i+1) for i in range(N-1)]
    rows = range(0,N-1)
    columns = range(1,N)
    n = sp.csc_matrix((data, (rows, columns)), shape=(N, N))
    return n if sparse == True else n.toarray()

def create(N, sparse=True):
    data = [np.sqrt(i+1) for i in range(N-1)]
    rows = range(1,N)
    columns = range(0,N-1)
    n = sp.csc_matrix((data, (rows, columns)), shape=(N, N))
    return n if sparse == True else n.toarray()

def identity(N, sparse=True):
    return sp.identity(N, format="csc") if sparse == True else np.identity(N)

def sigmay(N=2, sparse=True):
    data = [-1j, 1j]
    rows = [0, 1]
    columns = [1, 0]
    n =  sp.csc_matrix((data, (rows, columns)), shape=(2, 2))
    return n if sparse == True else n.toarray()

def sigmax(N=2, sparse=True):
    data = [1, 1]
    rows = [0, 1]
    columns = [1, 0]
    n = sp.csc_matrix((data, (rows, columns)), shape=(2, 2))
    return n if sparse == True else n.toarray()

def sigmaz(N=2, sparse=True):
    data = [1, -1]
    rows = [0, 1]
    columns = [0, 1]
    n = sp.csc_matrix((data, (rows, columns)), shape=(2, 2))
    return n if sparse == True else n.toarray()

def sigmap(N=2, sparse=True):
    data = [1]
    rows = [0]
    columns = [1]
    n = sp.csc_matrix((data, (rows, columns)), shape=(2, 2))
    return n if sparse == True else n.toarray()

def sigmam(N=2, sparse=True):
    data = [1]
    rows = [1]
    columns = [0]
    n = sp.csc_matrix((data, (rows, columns)), shape=(2, 2))
    return n if sparse == True else n.toarray()

def paritySUM(N, sparse=True):
    a = np.empty((N,))
    a[::2] = 1
    a[1::2] = -1
    data = a
    rows = range(0,N)
    columns = range(0,N)
    n = sp.csc_matrix((data,(rows,columns)), shape=(N,N))
    return n if sparse == True else n.toarray()

def parityEXP(HamiltonianCavity):
    sparse = sp.isspmatrix(HamiltonianCavity)
    parEX = ((1j * np.pi) * HamiltonianCavity.toarray())
    n = linA.expm(parEX)
    return sp.csc_matrix(n) if sparse == True else n

def basis(dimension, state, sparse=True):
    data = [1]
    rows = [state]
    columns = [0]
    n = sp.csc_matrix((data, (rows, columns)), shape=(dimension, 1))
    return n if sparse == True else n.toarray()

def maxLevel(dimension, sparse=True):
    n = (basis(dimension, dimension - 1, sparse=True) @
          (basis(dimension, dimension - 1, sparse=True).getH()))
    return n if sparse == True else n.toarray()

def displacement(alpha, dim, sparse=True):
    oper = (alpha * create(dim)) - (np.conj(alpha) * destroy(dim))
    n = linA.expm(oper.toarray())
    return sp.csc_matrix(n) if sparse == True else n

def squeeze(alpha, dim,sparse=True):
    oper = -(alpha * (create(dim)@create(dim))) + (np.conj(alpha) * (destroy(dim)@destroy(dim)))
    n = linA.expm(0.5*(oper.toarray()))
    return sp.csc_matrix(n) if sparse == True else n

def Jz(j,sparse=True, isDim=False):
    d = int((2*j) + 1)
    if isDim == True:
        d = j
    data = [j-i for i in range(d)]
    rows = range(0,d)
    columns = range(0,d)
    n = sp.csc_matrix((data, (rows, columns)), shape=(d, d))
    return n if sparse == True else n.toarray()

def Jp(j,sparse=True, isDim=False):
    d = int((2*j) + 1)
    if isDim == True:
        d = j
    d = int((2*j) + 1)
    m = [j-i for i in range(d)]
    data = [np.sqrt((j+m[i])*(j-m[i]+1)) for i in range(len(m) - 1)]
    rows = range(0,d-1)
    columns = range(1,d)
    n = sp.csc_matrix((data, (rows, columns)), shape=(d, d))
    return n if sparse == True else n.toarray()

def Jm(j,sparse=True, isDim=False):
    d = int((2*j) + 1)
    if isDim == True:
        d = j
    d = int((2*j) + 1)
    m = [j-i for i in range(d)]
    data = [np.sqrt((j+m[i])*(j-m[i]+1)) for i in range(len(m) - 1)]
    rows = range(1,d)
    columns = range(0,d-1)
    n = sp.csc_matrix((data, (rows, columns)), shape=(d, d))
    return n if sparse == True else n.toarray()

def Jx(j,sparse=True, isDim=False):
    n = 0.5*(Jp(j, isDim=isDim) + Jm(j, isDim=isDim))
    return n if sparse == True else n.toarray()

def Jy(k,sparse=True, isDim=False):
    n = (1/(2j))*(Jp(k, isDim=isDim) - Jm(k, isDim=isDim))
    return n if sparse == True else n.toarray()

def Js(j,sparse=True, isDim=False):
    n = (Jx(j, isDim=isDim)@Jx(j, isDim=isDim)) + (Jy(j, isDim=isDim)@Jy(j, isDim=isDim)) + (Jz(j, isDim=isDim)@Jz(j, isDim=isDim))
    return n if sparse == True else n.toarray()