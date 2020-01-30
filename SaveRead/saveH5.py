import h5py
import os
from datetime import datetime


def __dirNew(subs,rootDir):
    if isinstance(subs, str) == True:
        if not os.path.isdir(path):
            os.mkdir(path)
    else:
        for subDir in subs:
            __dirNew(subDir)
        


def makeDir(timestamp='', RootPath='/Users/cahitkargi/Dropbox/PhD/Numerical Results/'):
    if timestamp == '':
        now = datetime.now()
        date_time = now.strftime("%Y-%m-%d")
        year = fdate.strftime("%Y")
    else:
        fdate = datetime.fromtimestamp(timestamp)
        year = fdate.strftime("%Y")
        date_time = fdate.strftime("%Y-%m-%d")

    path = RootPath + year
    if not os.path.isdir(path):
        os.mkdir(path)

    path = path + date_time

    if not os.path.isdir(path):
        os.mkdir(path)

    return path

def saveData(dictionary, timestamp='', irregular=False, attribbutes={}):
    if timestamp == '':
        now = datetime.now()
        timestamp = datetime.timestamp(now)

    path = makeDir(timestamp)

    file = h5py.File(path + '/' + str(timestamp) + '.h5', 'w')
    writeAttr(file, attribbutes)

    if irregular == True:
        for key, value in dictionary.items():
            k = file.create_group(key)
            for irty in range(len(value)):
                k.create_dataset(str(irty), data=value[irty])
    else:
        for key, value in dictionary.items():
            file.create_dataset(key, data=value)

    file.close()
    return path


def writeAttr(k, attribbutes):
    for kk, vv in attribbutes.items():
        if isinstance(vv, dict):
            pass
        else:
            k.attrs[kk] = vv

def readData(timestamp, key = '', RootPath='/Users/cahitkargi/Dropbox/PhD/Numerical Results/'):
    fdate = datetime.fromtimestamp(timestamp)
    date = fdate.strftime("%Y-%m-%d")
    year = fdate.strftime("%Y")
    path = RootPath + '/'+ year + '/' + date + '/' + str(timestamp) + '.h5'
    f = h5py.File(path, 'r')
    return f if key == '' else list(f[key])
