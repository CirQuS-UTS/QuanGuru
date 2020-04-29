import numpy as np
import qTools.QuantumToolbox.evolution as lio
from qTools.QuantumToolbox.operators import identity
from qTools.classes.timeBase import timeBase
from qTools.classes.updateBase import updateBase
from qTools.classes.QUni import qUniversal

# under construction

class genericProtocol(timeBase):
    instances = 0
    label = 'genericProtocol'
    _boolDict = {}

    __slots__ = ['__unitary', 'lastState', '_allBools', '__inProtocol']
    def __init__(self, **kwargs):
        super().__init__(name=kwargs.pop('name', None))
        self.__unitary = None
        self.lastState = None
        self.__inProtocol = False
        self._allBools = genericProtocol._boolDict
        self._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member
        self._allBools = genericProtocol._boolDict
        self._allBools[self] = self._paramUpdated

    def save(self):
        saveDict = super().save()
        stepsDict = {}
        for sys in self.subSys.values():
            stepsDict[sys.name] = sys.save()
        saveDict['steps'] = stepsDict
        return saveDict

    def getUnitary(self):
        pass

    @property
    def unitary(self):
        if self._genericProtocol__unitary is not None:
            if ((self.superSys._paramUpdated is True) and (self.bound._paramUpdated is True)): # pylint: disable=no-member
                self._timeBase__paramUpdated = True # pylint: disable=assigning-non-slot
                self._allBools[self] = True

            if self._paramUpdated is False:
                unitary = self._genericProtocol__unitary
            else:
                unitary = self.getUnitary() # pylint: disable=assignment-from-no-return
                self._timeBase__paramUpdated = False  # pylint: disable=assigning-non-slot
                self._allBools[self] = False
        else:
            self._timeBase__paramUpdated = False  # pylint: disable=assigning-non-slot
            self._allBools[self] = False
            unitary = self.getUnitary() # pylint: disable=assignment-from-no-return

        if not any(list(self._allBools.values())):
            for sys in self._allBools:
                sys.superSys._paramUpdated = False
                sys._paramUpdated = False
        return unitary

    def delMatrices(self):
        self._genericProtocol__unitary = None # pylint: disable=assigning-non-slot

class qProtocol(genericProtocol):
    instances = 0
    label = 'qProtocol'

    __slots__ = []
    def __init__(self, **kwargs):
        super().__init__(name=kwargs.pop('name', None))
        self._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member

    @property
    def system(self):
        return self.superSys

    @system.setter
    def system(self, supSys):
        genericProtocol.superSys.fset(self, supSys) # pylint: disable=no-member

    @property
    def steps(self):
        return self._qUniversal__subSys # pylint: disable=no-member

    @steps.setter
    def steps(self, stps):
        self.addStep(*stps)

    def addStep(self, *args):
        for step in args:
            if step._genericProtocol__inProtocol:
                super().addSubSys(copyStep(step))
            else:
                super().addSubSys(step)
                step._genericProtocol__inProtocol = True
                # TODO is this really necessary ?
                if step.superSys is None:
                    step.superSys = self.superSys

    def createStep(self, n=1):
        newSteps = []
        for _ in range(n):
            newSteps.append(super().createSubSys(Step()))
        return newSteps if n > 1 else newSteps[0]

    def getUnitary(self):
        super().getUnitary()
        unitary = identity(self.superSys.dimension) # pylint: disable=no-member
        for step in self.steps.values():
            unitary = step.getUnitary() @ unitary
        self._genericProtocol__unitary = unitary # pylint: disable=assigning-non-slot
        return unitary

    def prepare(self, obj):
        super().prepare(obj)
        for step in self.steps.values():
            if not isinstance(step, copyStep):
                step.prepare(self)
                if not isinstance(step, qProtocol):
                    if step.fixed is True:
                        for update in step._Step__updates: # pylint: disable=protected-access
                            update.setup()
                        step.createUnitary()
                        for update in step._Step__updates: # pylint: disable=protected-access
                            update.setback()

    def delMatrices(self):
        super().delMatrices()
        for step in self.steps.values():
            if not isinstance(step, copyStep):
                step.delMatrices()

class Step(genericProtocol):
    instances = 0
    label = 'Step'
    __slots__ = ['__ratio', '__updates', '__fixed']
    def __init__(self, **kwargs):
        super().__init__(name=kwargs.pop('name', None))
        self.__ratio = None
        self.__updates = []
        self.__fixed = False
        self._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member

    @property
    def system(self):
        return self.superSys

    @system.setter
    def system(self, supSys):
        genericProtocol.superSys.fset(self, supSys) # pylint: disable=no-member
        if supSys is not None:
            if hasattr(self.superSys, '_genericQSys__unitary'):
                if self is self.superSys._genericQSys__unitary: # pylint: disable=no-member
                    self.qRes.name = self.superSys.name + 'Results' # pylint: disable=no-member
            else:
                self.qRes.name = self.superSys.name + self.name + 'Results' # pylint: disable=no-member

    @genericProtocol.superSys.setter # pylint: disable=no-member
    def superSys(self, supSys):
        genericProtocol.superSys.fset(self, supSys) # pylint: disable=no-member
        if supSys is not None:
            if hasattr(self.superSys, '_genericQSys__unitary'):
                if self is self.superSys._genericQSys__unitary: # pylint: disable=no-member
                    self.qRes.name = self.superSys.name + 'Results' # pylint: disable=no-member
            else:
                self.qRes.name = self.superSys.name + self.name + 'Results' # pylint: disable=no-member

    @property
    def updates(self):
        return self._Step__updates

    @property
    def ratio(self):
        return self._Step__ratio

    @ratio.setter
    def ratio(self, val):
        self._Step__ratio = val # pylint: disable=assigning-non-slot

    @property
    def fixed(self):
        return self._Step__fixed

    @fixed.setter
    def fixed(self, boolean):
        self._Step__fixed = boolean # pylint: disable=assigning-non-slot

    def getUnitary(self):
        super().getUnitary()
        if ((self.superSys._paramUpdated is True) or (self.bound._paramUpdated is True)): # pylint: disable=no-member
            self._timeBase__paramUpdated = True # pylint: disable=assigning-non-slot
            self._allBools[self] = True

        if self.fixed is True:
            if self._genericProtocol__unitary is None: # pylint: disable=no-member
                for update in self._Step__updates:
                    update.setup()
                self._genericProtocol__unitary = self.createUnitary()  # pylint: disable=assignment-from-no-return, assigning-non-slot
                for update in self._Step__updates:
                    update.setback()
            self._timeBase__paramUpdated = False # pylint: disable=assigning-non-slot
            self._allBools[self] = False
            unitary = self._genericProtocol__unitary # pylint: disable=no-member
        elif ((self._paramUpdated is False) and (self._genericProtocol__unitary is not None)): # pylint: disable=no-member
            unitary = self._genericProtocol__unitary # pylint: disable=no-member
        else:
            self._timeBase__paramUpdated = False # pylint: disable=assigning-non-slot
            self._allBools[self] = False
            for update in self._Step__updates:
                update.setup()
            unitary = self.createUnitary() # pylint: disable=assignment-from-no-return
            for update in self._Step__updates:
                update.setback()
        return unitary

    def createUpdate(self, **kwargs):
        update = Update(**kwargs)
        self.addUpdate(update)
        return update

    def addUpdate(self, *args):
        for update in args:
            self._Step__updates.append(update)

    def createUnitary(self):
        pass

    def prepare(self, obj):
        super().prepare(obj)
        if self.ratio is None:
            self.ratio = 1

class copyStep(qUniversal):
    instances = 0
    label = 'copyStep'

    __slots__ = []
    def __init__(self, superSys, **kwargs):
        super().__init__(name=kwargs.pop('name', None))
        self.superSys = superSys
        self._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member

    def save(self):
        saveDict = super().save()
        saveDict['superSys'] = self.superSys.name
        return saveDict

    def getUnitary(self):
        return self.superSys._genericProtocol__unitary

class freeEvolution(Step):
    instances = 0
    label = 'freeEvolution'
    __slots__ = []
    def __init__(self, **kwargs):
        super().__init__(name=kwargs.pop('name', None))
        self._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member

    def createUnitary(self):
        super().createUnitary()
        unitary = lio.LiouvillianExp(2 * np.pi * self.superSys.totalHam, timeStep=((self.stepSize*self.ratio)/self.samples)) # pylint: disable=no-member
        self._genericProtocol__unitary = unitary # pylint: disable=assigning-non-slot
        return unitary

class Gate(Step):
    instances = 0
    label = 'Gate'
    __slots__ = ['__implementation']
    def __init__(self, **kwargs):
        super().__init__(name=kwargs.pop('name', None))
        self.__implementation = None
        self._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member

    @property
    def implementation(self):
        return self._Gate__implementation

    @implementation.setter
    def implementation(self, typeStr):
        self._Gate__implementation = typeStr # pylint: disable=assigning-non-slot

class Update(updateBase):
    instances = 0
    label = 'Update'

    toBeSaved = qUniversal.toBeSaved.extendedCopy(['value'])

    __slots__ = ['value', '__memoryValue', '__memoryBool']
    def __init__(self, **kwargs):
        super().__init__(name=kwargs.pop('name', None))
        self.value = None
        self.__memoryValue = None
        self.__memoryBool = []
        self._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member

    def setup(self):
        for sys in self.subSys.values():
            self._Update__memoryValue = getattr(sys, self.key) # pylint: disable=assigning-non-slot
            self._Update__memoryBool.append(sys._paramUpdated)
        super()._runUpdate(self.value)

    def setback(self):
        for ind, sys in enumerate(self.subSys.values()):
            sys._paramUpdated = self._Update__memoryBool[ind]
        self._Update__memoryBool = [] # pylint: disable=assigning-non-slot
        super()._runUpdate(self._Update__memoryValue)
