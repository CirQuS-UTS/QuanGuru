import h5py
import os
from datetime import datetime
import scipy.sparse as sp


def saveData(dictionary, timestamp='', irregular=False, RootPath='/Users/cahitkargi/Dropbox/PhD/Numerical Results/'):
    now = datetime.now()
    date_time = now.strftime("%Y-%m-%d")
    path = RootPath + date_time

    if timestamp == '':
        timestamp =datetime.timestamp(now)

    if not os.path.isdir(path):
        os.mkdir(path)

    file = h5py.File(path + '/' + str(timestamp) + '.h5', 'w')

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


def readData(timestamp, key = '', RootPath='/Users/cahitkargi/Dropbox/PhD/Numerical Results/'):
    fdate = datetime.fromtimestamp(timestamp)
    date = fdate.strftime("%Y-%m-%d")
    path = RootPath + '/' + date + '/'+ str(timestamp) + '.h5'
    f = h5py.File(path, 'r')
    return f if key == '' else list(f[key])
