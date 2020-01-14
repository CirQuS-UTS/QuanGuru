import scipy.sparse as sp
import scipy.linalg as linA
import numpy as np

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

def Jz(j,sparse=True):
    d = int((2*j) + 1)
    data = [j-i for i in range(d)]
    rows = range(0,d)
    columns = range(0,d)
    n = sp.csc_matrix((data, (rows, columns)), shape=(d, d))
    return n if sparse == True else n.toarray()

def Jp(j,sparse=True):
    d = int((2*j) + 1)
    m = [j-i for i in range(d)]
    data = [np.sqrt((j+m[i])*(j-m[i]+1)) for i in range(len(m) - 1)]
    rows = range(0,d-1)
    columns = range(1,d)
    n = sp.csc_matrix((data, (rows, columns)), shape=(d, d))
    return n if sparse == True else n.toarray()

def Jm(j,sparse=True):
    d = int((2*j) + 1)
    m = [j-i for i in range(d)]
    data = [np.sqrt((j+m[i])*(j-m[i]+1)) for i in range(len(m) - 1)]
    rows = range(1,d)
    columns = range(0,d-1)
    n = sp.csc_matrix((data, (rows, columns)), shape=(d, d))
    return n if sparse == True else n.toarray()

def Jx(j,sparse=True):
    n = 0.5*(Jp(j) + Jm(j))
    return n if sparse == True else n.toarray()

def Jy(k,sparse=True):
    n = (1/(2j))*(Jp(k) - Jm(k))
    return n if sparse == True else n.toarray()

def Js(j,sparse=True):
    n = (Jx(j)@Jx(j)) + (Jy(j)@Jy(j)) + (Jz(j)@Jz(j))
    return n if sparse == True else n.toarray()