# TODO turn prints into actual error raise, they are print for testing

def qSystemInitErrors(init):
    def new_function(obj, **kwargs):
        init(obj, **kwargs)
        if obj.dimension is None:
            className = obj.__class__.__name__
            print(className + ' requires a dimension')
        elif obj.frequency is None:
            className = obj.__class__.__name__
            print(className + ' requires a frequency')
    return new_function


def qCouplingInitErrors(init):
    def new_function(obj, *args, **kwargs):
        init(obj, *args, **kwargs)
        if obj._qCoupling__cFncs is None:
            className = obj.__class__.__name__
            print(className + ' requires a coupling functions')
        elif obj._qCoupling__qSys is None:
            className = obj.__class__.__name__
            print(className + ' requires a coupling systems')
        
        '''for ind in range(len(obj._qCoupling__qSys)):
            if len(obj._qCoupling__cFncs) != len(obj._qCoupling__qSys):
                className = obj.__class__.__name__
                print(className + ' requires same number of systems as coupling functions')'''

    return new_function


def sweepInitError(init):
    def new_function(obj, **kwargs):
        init(obj, **kwargs)
        if obj.sweepList is None:
            className = obj.__class__.__name__
            print(className + ' requires either a list or relevant info, here are givens' 
            + '\n' + 
            'sweepList: ', obj.sweepList, '\n' +
            'sweepMax: ', obj.sweepMax, '\n' +
            'sweepMin: ',obj.sweepMin, '\n' +
            'sweepPert: ', obj.sweepPert, '\n' +
            'logSweep: ', obj.logSweep)

    return new_function
