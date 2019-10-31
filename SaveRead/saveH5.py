import h5py
import os
from datetime import datetime


def makeDir(timestamp='', RootPath='/Users/cahitkargi/Dropbox/PhD/Numerical Results/'):
    if timestamp == '':
        now = datetime.now()
        date_time = now.strftime("%Y-%m-%d")
    else:
        fdate = datetime.fromtimestamp(timestamp)
        date_time = fdate.strftime("%Y-%m-%d")

    path = RootPath + date_time

    if not os.path.isdir(path):
        os.mkdir(path)

    return path

def saveData(dictionary, timestamp='', irregular=False,attribbutes={}):
    if timestamp == '':
        now = datetime.now()
        timestamp = datetime.timestamp(now)

    path = makeDir(timestamp)

    file = h5py.File(path + '/' + str(timestamp) + '.h5', 'w')
    writeAttr(file, attribbutes)

    if irregular == True:
        for key, value in dictionary.items():
            k = file.create_group(key)
            for i in range(len(value)):
                k.create_dataset(str(i), data=value[i])
    else:
        for key, value in dictionary.items():
            file.create_dataset(key, data=value)

    file.close()
    return path


def writeAttr(k, attribbutes):
    for kkk, vvv in attribbutes.items():
        if isinstance(vvv, dict):
            pass
        else:
            k.attrs[kkk] = vvv

def readData(timestamp, key = '', RootPath='/Users/cahitkargi/Dropbox/PhD/Numerical Results/'):
    fdate = datetime.fromtimestamp(timestamp)
    date = fdate.strftime("%Y-%m-%d")
    path = RootPath + '/' + date + '/'+ str(timestamp) + '.h5'
    f = h5py.File(path, 'r')
    return f if key == '' else list(f[key])
