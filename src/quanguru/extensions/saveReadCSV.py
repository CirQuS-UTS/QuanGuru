r"""
    Contains data saving (into CSV) functions.

    .. currentmodule:: quanguru.extensions.saveReadCSV

    Functions
    ---------

    .. autosummary::

        saveCSV
        readCSV
        saveQResCSV
        _recursiveSaveList
        _saveDictToCSV

    .. |c| unicode:: U+2705
    .. |x| unicode:: U+274C
    .. |w| unicode:: U+2000

    =======================    ==================   ==============   ================   ===============
       **Function Name**        **Docstrings**       **Examples**     **Unit Tests**     **Tutorials**
    =======================    ==================   ==============   ================   ===============
      `saveCSV`                  |w| |w| |w| |c|      |w| |w| |x|      |w| |w| |x|        |w| |w| |x|
      `readCSV`                  |w| |w| |w| |c|      |w| |w| |x|      |w| |w| |x|        |w| |w| |x|
      `saveQResCSV`              |w| |w| |w| |x|      |w| |w| |x|      |w| |w| |x|        |w| |w| |x|
      `_recursiveSaveList`       |w| |w| |w| |x|      |w| |w| |x|      |w| |w| |x|        |w| |w| |x|
      `_saveDictToCSV`           |w| |w| |w| |x|      |w| |w| |x|      |w| |w| |x|        |w| |w| |x|
    =======================    ==================   ==============   ================   ===============
"""

import csv
from datetime import datetime
import numpy as np
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

    with open(path + '/' + str(fileName) + '.txt', 'w') as csvFile: #pylint:disable=W1514
        csvWriter = csv.writer(csvFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        if isinstance(data[0], (list, np.ndarray)):
            for ind in range(len(data)):
                csvWriter.writerow([data[ind][ind2] for ind2 in range(len(data[ind]))])
        elif isinstance(data[0], (float, int, np.complex128)):
            csvWriter.writerow([data[ind2] for ind2 in range(len(data))])

    return path

def readCSV(path, datatype=float, realVal=True):
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
    with open(path) as csvFile: #pylint:disable=W1514
        csvReader = csv.reader(csvFile, delimiter=',')
        lineCount = 0
        for row in csvReader:
            lineCount += 1
            if datatype != np.complex128:
                data.append(np.array(list(row), dtype=datatype))
            else:
                li = np.genfromtxt(list(row), delimiter=',', dtype=np.complex)
                data.append(np.real(li) if realVal else li)
    return data if len(data) > 1 else data[0]

def _recursiveSaveList(data, path=None, fileName=None):
    if isinstance(data[0], (list, np.ndarray)):
        if isinstance(data[0][0], (list, np.ndarray)):
            for ind in range(len(data)): #pylint:disable=consider-using-enumerate
                _recursiveSaveList(data[ind], path=path, fileName=fileName+str(ind))
        elif isinstance(data[0][0], (float, int, np.complex128)):
            saveCSV(data, path=path, fileName=fileName)
    elif isinstance(data[0], (float, int, np.complex128)):
        saveCSV(data[0], path=path, fileName=fileName)

def _saveDictToCSV(data, path=None, fileName=''):
    for key, val in data.items():
        _recursiveSaveList(val, path, fileName=fileName+key)

def saveQResCSV(qRes, path=None):
    results = qRes.allResults
    for key, val in results.items():
        result = val.results
        if len(result.keys()) > 0:
            _saveDictToCSV(result, path, key._allStringSum()) #pylint:disable=protected-access
