"""
    THESE ARE JUST SOME INITIAL IDEAS. NOT COMPLETED OR USED YET.

    .. currentmodule:: quanguru.classes.exceptions

    .. autosummary::

        qSystemInitErrors
        qCouplingInitErrors
        sweepInitError

"""
def raiseAttrType(attrName, expectedTypes):
    def decorate(f):
        def typeCheck(obj, *args, **kwargs):
            val = kwargs.get(attrName, None)
            if not any(isinstance(val, t) for t in expectedTypes): raise TypeError("name should be a string") #pylint:disable=multiple-statements
            f(obj, *args, **kwargs)
        return typeCheck
    return decorate

# TODO turn prints into actual error raise, they are print for testing

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
