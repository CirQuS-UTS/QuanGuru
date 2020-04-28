import os
import sys
from datetime import datetime
import h5py
from qTools.classes.QRes import qResults

def makeDir(path=None):
    if path is None:
        path = sys.path[0]

    if not os.path.isdir(path):
        os.mkdir(path)

    return path

def saveH5(dictionary, fileName=None, attributes=dict, path=None, irregular=False): # pylint: disable=invalid-name
    if fileName is None:
        now = datetime.now()
        fileName = datetime.timestamp(now)
    path = makeDir(path)

    file = h5py.File(path + '/' + str(fileName) + '.h5', 'w')
    if isinstance(attributes, dict):
        writeAttr(file, attributes, path, fileName)

    if irregular is True:
        for key, value in dictionary.items():
            k = file.create_group(key)
            for irty, val in enumerate(value):
                k.create_dataset(str(irty), data=val)
    else:
        for key, value in dictionary.items():
            file.create_dataset(key, data=value)

    file.close()
    return path, fileName


def _reDict(inp, i=0, retDict={}, keyDict=None): # pylint: disable=dangerous-default-value
    for key, val in inp.items():
        if key in retDict.keys():
            key = key + keyDict
            if key in retDict.keys():
                key = key + keyDict + '_' + str(i)
                i += 1

        if isinstance(val, dict):
            retDict[key + '_'] = '|'
            _reDict(val, i, retDict, keyDict=key)
        else:
            retDict[key] = val
    return retDict

def writeToTxt(path, timestamp, saveDict):
    saveName = path + '/' + str(timestamp) + '.txt'
    with open(saveName, 'w') as f:
        f.write(' \n'.join(["%s = %s" % (k, v) for k, v in saveDict.items()]))

def writeAttr(k, attributes, path, name):
    attributes = _reDict(attributes)
    #print(attributes)
    writeToTxt(path, name, attributes)

    for key, val in attributes.items():
        #print(key, val)
        if val != '|':
            k.attrs[key] = val
    return k

def readH5(path, fileName, key=None): # pylint: disable=invalid-name
    path = path + '/' + fileName + '.h5'
    f = h5py.File(path, 'r')
    return f if key is None else list(f[key])

def readH5toDict(path, fileName): # pylint: disable=invalid-name
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
            rDict = {}
            for key1, val1 in val.items():
                try:
                    _rDict = {}
                    for key2, val2 in val1.items():
                        _rDict[key2] = list(val2)
                    rDict[key1] = _rDict
                except: # pylint: disable=bare-except
                    rDict[key1] = list(val1)
            resDict[key] = rDict
    return resDict, f.attrs

def saveAll(qRes, fileName=None, attributes=dict, path=None, irregular=False):
    if fileName is None:
        now = datetime.now()
        fileName = datetime.timestamp(now)

    path = makeDir(path)

    file = h5py.File(path + '/' + str(fileName) + '.h5', 'w')
    if isinstance(attributes, dict):
        writeAttr(file, attributes, path, fileName)

    for value1 in qRes.allResults.values():
        k = file.create_group(value1.name)
        dictionary = value1.results
        if irregular is True:
            for key, value in dictionary.items():
                k2 = k.create_group(key)
                for irty, val in enumerate(value):
                    k2.create_dataset(str(irty), data=val)
        else:
            for key, value in dictionary.items():
                k.create_dataset(key, data=value)

    file.close()
    return path, fileName


def _qResSaveH5(qRes, fileName=None, attributes=dict, path=None, irregular=False): # pylint: disable=invalid-name
    p, f = saveH5(qRes.results, fileName, attributes, path, irregular)
    return p, f

qResults.saveAll = saveAll
qResults.saveH5 = _qResSaveH5
