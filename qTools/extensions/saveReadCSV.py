import csv
import numpy as np
from datetime import datetime
from ._helpers import makeDir

def saveCSV(data, path=None, fileName=None):
    """
    Function to write the given data into a CSV file. Single list of data is written as a single row. If the data is
    list of list, each list is written as a row. This approach is adopted to make it compatible with step size sweeps
    that creates a list of lists each with different length.

    Parameters
    ----------
    data : list
        data to be saved into CSV
    path : str, optional
        path to save the CSV file, by default None, which saves into the current working directory
    fileName : str, optional
        name for the CSV file, by default None for which a time stamp is used as the name

    Returns
    -------
    str
        path to the saved CSV file
    """

    if fileName is None:
        now = datetime.now()
        fileName = datetime.timestamp(now)
    path = makeDir(path)

    with open(path + '/' + str(fileName) + '.txt', 'w') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        if isinstance(data[0], (list, np.ndarray)):
            for ind in range(len(data)):
                csv_writer.writerow([data[ind][ind2] for ind2 in range(len(data[ind]))])
        elif isinstance(data[0], (float, int, np.complex128)):
            csv_writer.writerow([data[ind2] for ind2 in range(len(data))])

    return path

def readCSV(path, datatype=float):
    """
    Function to read from a CSV file in the given path. Rows of the CSV file are read in as list into an arrays.

    Parameters
    ----------
    path : str
        path to the CSV file

    Returns
    -------
    list
        list containing the data read from the CSV file
    """

    data = []
    with open(path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            line_count += 1
            if datatype != np.complex128:
                data.append(np.array(list(row), dtype=datatype))
            else:
                li = np.genfromtxt(list(row), delimiter=',', dtype=np.complex)
                data.append(np.real(li))
    return data if len(data) > 1 else data[0]

def _recursiveSaveList(data, path=None, fileName=None):
    if isinstance(data[0], (list, np.ndarray)):
        if isinstance(data[0][0], (list, np.ndarray)):
            for ind in range(len(data)):
                _recursiveSaveList(data[ind], path=path, fileName=fileName+str(ind))
        elif isinstance(data[0][0], (float, int, np.complex128)):
            saveCSV(data, path=path, fileName=fileName)
    elif isinstance(data[0], (float, int, np.complex128)):
        saveCSV(data[0], path=path, fileName=fileName)

def _saveDictToCSV(data, path=None, fileName=None):
    for key, val in data.items():
        _recursiveSaveList(val, path, fileName=fileName+key)

def saveQResCSV(qRes, path=None):
    results = qRes.allResults
    for key, val in results.items():
        result = val.results
        if len(result.keys()) > 0:
            _saveDictToCSV(result, path, key._allStringSum())
