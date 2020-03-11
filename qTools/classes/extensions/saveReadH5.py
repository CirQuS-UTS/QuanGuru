import h5py
import os
import sys
from datetime import datetime

def makeDir(RootPath=None):
    if RootPath is None:
        RootPath = sys.path[0]

    if not os.path.isdir(RootPath):
        os.mkdir(RootPath)

    return RootPath

def saveH5(dictionary, fileName=None, irregular=False, attributes=dict, RootPath=None):
    if fileName is None:
        now = datetime.now()
        fileName = datetime.timestamp(now)

    path = makeDir(RootPath)

    file = h5py.File(path + '/' + str(fileName) + '.h5', 'w')
    writeAttr(file, attributes)

    if irregular is True:
        for key, value in dictionary.items():
            k = file.create_group(key)
            for irty in range(len(value)):
                k.create_dataset(str(irty), data=value[irty])
    else:
        for key, value in dictionary.items():
            file.create_dataset(key, data=value)

    file.close()
    return path, fileName


def writeAttr(k, attribbutes):
    for kk, vv in attribbutes.items():
        if isinstance(vv, dict):
            writeAttr(k, vv)
        else:
            k.attrs[kk] = vv

def readH5(fileName, path, key = None):
    path = path + '/' + fileName + '.h5'
    f = h5py.File(path, 'r')
    return f if key is None else list(f[key])
