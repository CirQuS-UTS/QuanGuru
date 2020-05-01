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
        if obj._qCoupling__cFncs is None: # pylint: disable=protected-access
            className = obj.__class__.__name__
            print(className + ' requires a coupling functions')
        elif obj._qCoupling__qSys is None: # pylint: disable=protected-access
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
                  + '\n' +
                  'sweepList: ', obj.sweepList, '\n' +
                  'sweepMax: ', obj.sweepMax, '\n' +
                  'sweepMin: ', obj.sweepMin, '\n' +
                  'sweepPert: ', obj.sweepPert, '\n' +
                  'logSweep: ', obj.logSweep)

    return newFunction
