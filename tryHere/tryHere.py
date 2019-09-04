import numpy as np
import sys
import scipy.sparse as sp

def get_size(obj, seen=None):
    print(sp.isspmatrix(obj))
    size = sys.getsizeof(obj)
    if seen is None:
        seen = set()
    obj_id = id(obj)
    if obj_id in seen:
        return 0
    seen.add(obj_id)
    print(sp.isspmatrix(obj))
    print(hasattr(obj, '__dict__'))
    if isinstance(obj, dict):
        print('here')
        size += sum([get_size(v, seen) for v in obj.values()])
        size += sum([get_size(k, seen) for k in obj.keys()])
    elif hasattr(obj, '__dict__'):
        size += get_size(obj.__dict__, seen)
    elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
        size += sum([get_size(i, seen) for i in obj])
    return size

dim = 100

ls = [[2 for i in range(dim)] for j in range(dim)]
ss = sp.csc_matrix(ls)
print(ss)
print(type(ls))
ns = np.array(ls)
print(type(ns))
print(ns)
print(isinstance(ns, np.ndarray))
print(isinstance(ls, np.ndarray))

print(get_size(ss))