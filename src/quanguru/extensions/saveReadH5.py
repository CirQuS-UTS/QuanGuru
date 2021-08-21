# from datetime import datetime
# #import h5py
# from quanguru.classes.QRes import qResults
# from ._helpers import makeDir

# def _reDict(inp, i=0, retDict={}, keyDict=None): # pylint: disable=dangerous-default-value
#     for key, val in inp.items():
#         if key in retDict.keys():
#             key = key + keyDict
#             if key in retDict.keys():
#                 key = key + keyDict + '_' + str(i)
#                 i += 1

#         if isinstance(val, dict):
#             retDict[key + '_'] = '|'
#             _reDict(val, i, retDict, keyDict=key)
#         else:
#             retDict[key] = val
#     return retDict

# def writeToTxt(path, timestamp, saveDict):
#     saveName = path + '/' + str(timestamp) + '.txt'
#     with open(saveName, 'w') as f:
#         f.write(' \n'.join(["%s = %s" % (k, v) for k, v in saveDict.items()]))

# def writeAttr(k, attributes, path, name):
#     """
#     Method write a dictionary or dictionary of dictionaries into attributes to a `h5` file and also into a txt. It
#     first
#     converts the dictionary of dictionaries into a single dictionary, so if modifies any duplicate key.

#     Parameters
#     ----------
#     k : h5
#         `.h5` file to write the attributes
#     attributes : dict
#         a dictionary or dictionary of dictionaries to write as attributes and into a `.txt`
#     path : str
#         path for the `.txt` file
#     name : str
#         name for the `.txt` file

#     Returns
#     -------
#     h5
#         the given `.h5` file
#     """

#     # convertion to a single dictionary
#     attributes = _reDict(attributes)

#     writeToTxt(path, name, attributes)

#     for key, val in attributes.items():
#         #print(key, val)
#         if val != '|':
#             k.attrs[key] = val
#     return k

# def saveH5(dictionary, fileName=None, attributes=dict, path=None, irregular=False): # pylint: disable=invalid-name
#     if fileName is None:
#         now = datetime.now()
#         fileName = datetime.timestamp(now)
#     path = makeDir(path)

#     file = h5py.File(path + '/' + str(fileName) + '.h5', 'w')
#     if isinstance(attributes, dict):
#         writeAttr(file, attributes, path, fileName)

#     if irregular is True:
#         for key, value in dictionary.items():
#             k = file.create_group(key)
#             for irty, val in enumerate(value):
#                 k.create_dataset(str(irty), data=val)
#     else:
#         for key, value in dictionary.items():
#             file.create_dataset(key, data=value)

#     file.close()
#     return path, fileName


# def readH5(path, fileName, key=None): # pylint: disable=invalid-name
#     path = path + '/' + fileName + '.h5'
#     f = h5py.File(path, 'r')
#     return f if key is None else list(f[key])

# def readH5toDict(path, fileName): # pylint: disable=invalid-name
#     path = path + '/' + fileName + '.h5'
#     f = h5py.File(path, 'r')
#     resDict = {}
#     for key, val in f.items():
#         resDict[key] = list(val)
#     return resDict

# def readAll(path, fileName):
#     path = path + '/' + fileName + '.h5'
#     f = h5py.File(path, 'r')
#     resDict = {}
#     for key, val in f.items():
#         if len(val) > 0:
#             rDict = {}
#             for key1, val1 in val.items():
#                 try:
#                     _rDict = {}
#                     for key2, val2 in val1.items():
#                         _rDict[key2] = list(val2)
#                     rDict[key1] = _rDict
#                 except: # pylint: disable=bare-except # noqa: E722
#                     rDict[key1] = list(val1)
#             resDict[key] = rDict
#     return resDict, f.attrs

# def saveAll(qRes, fileName=None, attributes=dict, path=None, irregular=False):
#     if fileName is None:
#         now = datetime.now()
#         fileName = datetime.timestamp(now)

#     path = makeDir(path)

#     file = h5py.File(path + '/' + str(fileName) + '.h5', 'w')
#     if isinstance(attributes, dict):
#         writeAttr(file, attributes, path, fileName)

#     for value1 in qRes.allResults.values():
#         k = file.create_group(value1.name)
#         dictionary = value1.results
#         if irregular is True:
#             for key, value in dictionary.items():
#                 k2 = k.create_group(key)
#                 for irty, val in enumerate(value):
#                     k2.create_dataset(str(irty), data=val)
#         else:
#             for key, value in dictionary.items():
#                 k.create_dataset(key, data=value)

#     file.close()
#     return path, fileName


# def _qResSaveH5(qRes, fileName=None, attributes=dict, path=None, irregular=False): # pylint: disable=invalid-name
#     p, f = saveH5(qRes.results, fileName, attributes, path, irregular)
#     return p, f

# qResults.saveAll = saveAll
# qResults.saveH5 = _qResSaveH5


# def _keySearch(sDict, sKey) -> bool:
#     boolean = False
#     if len(sDict) == 0:
#         boolean = False
#     elif isinstance(sDict, dict):
#         if sKey in sDict.keys():
#             if len(sDict[sKey]) == 0:
#                 boolean = False
#             elif isinstance(sDict[sKey], dict):
#                 boolean = _keySearch(sDict[sKey], list(sDict[sKey].keys())[0])
#             else:
#                 boolean = True
#         else:
#             boolean = False
#             for v in sDict.values():
#                 boolean = _keySearch(v, sKey)
#                 if boolean:
#                     break
#     return boolean

# def _readFrom(file, keyTo=None, oldDict=None, depth=-1, initial=-1): # pylint: disable=too-many-arguments
#     rDict = {}
#     if not _keySearch(oldDict, keyTo):
#         if hasattr(file, 'items'):
#             if depth != 0:
#                 if depth != initial:
#                     depth -= 1

#                 for key, val in file.items():
#                     if key == '0':
#                         break

#                     if keyTo == key:
#                         depth -= 1
#                         rDict[key], depth = _readFrom(val, keyTo=None, oldDict=oldDict, depth=depth,
#                                                       initial=initial)
#                     else:
#                         rDict[key], depth = _readFrom(val, keyTo=keyTo, oldDict=oldDict, depth=depth,
#                                                       initial=initial)
#             elif depth == 0:
#                 rList = []
#                 for ind in range(len(file.keys())):
#                     rList.append(list(file[str(ind)]))
#                 depth = initial
#                 rDict = rList
#         else:
#             rDict = list(file)
#             depth = initial
#     return rDict, depth

# def readFrom(qRes, file, readKey, depth=-1):
#     oldDict = qRes._qResBase__results
#     rDict, _ = _readFrom(file, keyTo=readKey, oldDict=oldDict, depth=depth, initial=depth)
#     qRes._qResBase__results = rDict
#     for k, v in oldDict.items():
#         if v not in [[], {}]:
#             qRes._qResBase__results[k] = v
#     qRes._qResBase__resultsLast = qRes._qResBase__results

# qResults.readFrom = readFrom
