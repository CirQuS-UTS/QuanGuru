import h5py
import os
import sys
from datetime import datetime
from qTools.classes.QRes import qResults

def makeDir(path=None):
    if path is None:
        path = sys.path[0]
    
    if not os.path.isdir(path):
        os.mkdir(path)

    return path

def saveH5(dictionary, fileName=None, attributes=dict, path=None, irregular=False):
    if fileName is None:
        now = datetime.now()
        fileName = datetime.timestamp(now)
    path = makeDir(path)

    file = h5py.File(path + '/' + str(fileName) + '.h5', 'w')
    if isinstance(attributes, dict):
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


def writeAttr(k, attributes):
    for kk, vv in attributes.items():
        if isinstance(vv, dict):
            writeAttr(k, vv)
        else:
            k.attrs[kk] = vv

def readH5(path, fileName, key = None):
    path = path + '/' + fileName + '.h5'
    f = h5py.File(path, 'r')
    return f if key is None else list(f[key])

def readH5toDict(path, fileName):
    path = path + '/' + fileName + '.h5'
    f = h5py.File(path, 'r')
    resDict = {}
    for key, val in f.items():
        resDict[key] = list(val)
    return resDict

def readAll(path, fileName):
    path = path + '/' + fileName + '.h5'
    f = h5py.File(path, 'r')
    resDict = {}
    for key, val in f.items():
        if len(val) > 0:
            rDict =  {}
            for key1, val1 in val.items():
                rDict[key1] = list(val1)
            resDict[key] = rDict
    return resDict

def saveAll(qRes, fileName=None, attributes=dict, path=None, irregular=False):
    if fileName is None:
        now = datetime.now()
        fileName = datetime.timestamp(now)

    path = makeDir(path)

    file = h5py.File(path + '/' + str(fileName) + '.h5', 'w')
    if isinstance(attributes, dict):
        writeAttr(file, attributes)

    for key1, value1 in qRes.allResults.items():
        k = file.create_group(key1)
        dictionary = value1.results
        if irregular is True:
            for key, value in dictionary.items():
                k = file.create_group(key)
                for irty in range(len(value)):
                    k.create_dataset(str(irty), data=value[irty])
        else:
            for key, value in dictionary.items():
                k.create_dataset(key, data=value)

    file.close()
    return path, fileName




def _qResSaveH5(qRes, fileName=None, attributes=dict, path=None, irregular=False):
    p, f = saveH5(qRes.results, fileName, attributes, path, irregular)
    return p, f

qResults.saveAll = saveAll
qResults.saveH5 = _qResSaveH5