import h5py
import os
from datetime import datetime
import scipy.sparse as sp


def saveData(dictionary, timestamp='', irregular=False, RootPath='/Users/cahitkargi/Dropbox/PhD/Numerical Results/'):
    now = datetime.now()
    date_time = now.strftime("%Y-%m-%d")
    path = RootPath + date_time

    if timestamp == '':
        timestamp = str(datetime.timestamp(now))

    if not os.path.isdir(path):
        os.mkdir(path)

    file = h5py.File(path + '/' + timestamp + '.h5', 'w')

    if irregular == True:
        for key, value in dictionary.items():
            k = file.create_group(key)
            for i in range(len(value)):
                if sp.isspmatrix(value):
                    value = value.toarray()
                k.create_dataset(str(i), data=value[i])
    else:
        for key, value in dictionary.items():
            if sp.isspmatrix(value):
                value = value.toarray()
            file.create_dataset(key, data=value)

    file.close()
    return path


def readData(timestamp, RootPath='/Users/cahitkargi/Dropbox/PhD/Numerical Results/'):
    print('I read an h5')
