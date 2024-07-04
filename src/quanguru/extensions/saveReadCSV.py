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

def _getDateTimeStamps():
    """
    Function to get date and time-stamp

    Returns
    -------
    tuple(str, str)
        tuple containing the datestamp and timestamp as strings
    """
    fullTS = datetime.now()
    ds = fullTS.strftime('%y%m%d')
    ts = fullTS.strftime('%H%M%S')

    return (ds, ts)

def _dateTime(fileName):
    """
    Function to add date and time-stamp into the file name.
    Data (as YY/MM/DD) is added as a prefix, and time-stamp (as HH/MM/SS) as suffix

    Parameters
    ----------
    fileName : str
        file name

    Returns
    -------
    str
        file name with data prefix and time-stamp suffix
    """
    ds, ts = _getDateTimeStamps()
    if fileName is None:
        fileName = ds + '_' + ts
    else:
        fileName = ds + "_" + fileName + '_' + ts
    return fileName

def saveCSV(data, path=None, fileName=None, dateTime=True):
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
    dateTime : bool, optional
        whether the filename should be bound by the datestamp and timestamp (according to _dateTime func) at time of 
        execution

    Returns
    -------
    str
        path to the saved CSV file
    """
    if dateTime:
        fileName = _dateTime(fileName)
    
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

def _recursiveSaveList(data, path=None, fileName=None, dateTimeStamps=None):
    if isinstance(data[0], (list, np.ndarray)):
        if isinstance(data[0][0], (list, np.ndarray)):
            for ind in range(len(data)): #pylint:disable=consider-using-enumerate
                _recursiveSaveList(data[ind], path=path, fileName=fileName+str(ind), dateTimeStamps=dateTimeStamps)
        elif isinstance(data[0][0], (float, int, np.complex128)):
            if dateTimeStamps is not None:
                fileName = dateTimeStamps[0] + '_' + fileName + '_' + dateTimeStamps[1]
            saveCSV(data, path=path, fileName=fileName, dateTime=False)
    elif isinstance(data[0], (float, int, np.complex128)):
        if dateTimeStamps is not None:
            fileName = dateTimeStamps[0] + '_' + fileName + '_' + dateTimeStamps[1]
        saveCSV(data, path=path, fileName=fileName, dateTime=False)

def _saveDictToCSV(data, path=None, fileName='', dateTimeStamps=None):
    for key, val in data.items():
        _recursiveSaveList(val, path, fileName=fileName+key, dateTimeStamps=dateTimeStamps)

def saveQResCSV(qRes, path=None, fileNamePrefix='', dateTime=True):
    dateTimeStamps = None
    if dateTime:
        dateTimeStamps = _getDateTimeStamps()
    results = qRes.allResults
    for key, val in results.items():
        result = val.resultsDict
        if len(result.keys()) > 0:
            _saveDictToCSV(result, path, fileNamePrefix+key._allStringSum(), dateTimeStamps) #pylint:disable=protected-access
