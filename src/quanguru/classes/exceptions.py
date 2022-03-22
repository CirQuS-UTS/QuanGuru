"""
    THESE ARE JUST SOME INITIAL IDEAS. NOT COMPLETED OR USED YET.

    .. currentmodule:: quanguru.classes.exceptions

    .. autosummary::

        qSystemInitErrors
        qCouplingInitErrors
        sweepInitError

"""
import warnings
from functools import wraps

def raiseAttrType(expectedTypes, attrName=0, attrPrintName=None):
    # if attrName is given as str, but that keyword is not passed/provided and type(None) is not in expectedTypes
    # this will raise the TypeError. Note that it needs to be passed in kwargs, otherwise will raise the TypeError
    # so, in general it is better to use it as int, but still you have to make sure that it is always passes in the
    # correct position.
    def decorate(f):
        @wraps(f)
        def typeCheck(obj, *args, **kwargs):
            val = kwargs.get(attrName, None)
            if isinstance(attrName, int):
                if attrName > len(args):
                    raise IndexError('Index ' + attrName + ' is larger than the number of args (' + len(args) + ') passed to the function ' + f.__name__) # pylint:disable=line-too-long
                val = args[attrName]
            else:
                raise TypeError('attrName should either be a string (to look up kwargs) or int (to look up in args)')

            if not isinstance(expectedTypes, (list, tuple, type)):
                raise TypeError('expectedTypes should either be a type of list/tuple of types')
            ct = any(isinstance(val, t) for t in expectedTypes) if isinstance(expectedTypes, (list, tuple)) else isinstance(val, expectedTypes) # pylint:disable=line-too-long
            if not ct:
                tNames = [str(ety) for ety in expectedTypes]
                aKey = attrName if isinstance(attrName, str) else f"{attrName}th argument"
                apn = attrPrintName if attrPrintName is not None else aKey
                msg = apn + " should be an instance of " + ", ".join(tNames) + f", but {type(val)} is given"
                raise TypeError(msg) #pylint:disable=multiple-statements
            return f(obj, *args, **kwargs)
        return typeCheck
    return decorate

def checkNotVal(someObj, val, msg):
    if someObj == val:
        raise ValueError(msg)
    return someObj

def checkVal(someObj, val, msg):
    if someObj != val:
        raise ValueError(msg)
    return someObj

def checkCorType(someObj, someType, msg):
    if isinstance(someType, list):
        for ty in someType:
            checkCorType(someObj, ty, msg)

    if not isinstance(someObj, someType):
        raise TypeError(msg + ' requires ' + str(someType) + ' but ' + str(type(someObj)) + ' is given.')
    return someObj

def attrNotTypeWarn(someAttr, someTypes, msg):
    if not isinstance(someAttr, someTypes):
        warnings.warn(msg)
    return someAttr

def attrNotValWarn(someAttr, someValue, msg):
    if someAttr != someValue:
        warnings.warn(msg)
    return someAttr

# turn prints into actual error raise, they are print for testing
def qSystemInitErrors(init):
    def newFunction(obj, **kwargs):
        init(obj, **kwargs)
        if obj._genericQSys__dimension is None:
            className = obj.__class__.__name__
            print(className + ' requires a dimension')
        elif obj.frequency is None:
            className = obj.__class__.__name__
            print(className + ' requires a frequency')
    return newFunction


def qCouplingInitErrors(init):
    def newFunction(obj, *args, **kwargs):
        init(obj, *args, **kwargs)
        if obj.couplingOperators is None: # pylint: disable=protected-access
            className = obj.__class__.__name__
            print(className + ' requires a coupling functions')
        elif obj.coupledSystems is None: # pylint: disable=protected-access
            className = obj.__class__.__name__
            print(className + ' requires a coupling systems')

        #for ind in range(len(obj._qCoupling__qSys)):
        #    if len(obj._qCoupling__cFncs) != len(obj._qCoupling__qSys):
        #        className = obj.__class__.__name__
        #        print(className + ' requires same number of systems as coupling functions')
    return newFunction


def sweepInitError(init):
    def newFunction(obj, **kwargs):
        init(obj, **kwargs)
        if obj.sweepList is None:
            className = obj.__class__.__name__
            print(className + ' requires either a list or relevant info, here are givens'
                  + '\n' +  # noqa: W503, W504
                  'sweepList: ', obj.sweepList, '\n' +  # noqa: W504
                  'sweepMax: ', obj.sweepMax, '\n' +  # noqa: W504
                  'sweepMin: ', obj.sweepMin, '\n' +  # noqa: W504
                  'sweepPert: ', obj.sweepPert, '\n' +  # noqa: W504
                  'logSweep: ', obj.logSweep)
    return newFunction
