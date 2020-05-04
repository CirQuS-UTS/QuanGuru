import numpy as np
import qTools.QuantumToolbox.evolution as lio
from qTools.QuantumToolbox.operators import identity
from qTools.classes.qBaseSim import qBaseSim
from qTools.classes.updateBase import updateBase
from qTools.classes.QUni import qUniversal

# under construction

class genericProtocol(qBaseSim):
    instances = 0
    label = 'genericProtocol'

    __slots__ = ['lastState', '__inProtocol', '__fixed']
    def __init__(self, **kwargs):
        super().__init__(name=kwargs.pop('name', None))
        self.lastState = None
        self.__inProtocol = False
        self.__fixed = False
        self._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member

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
    def fixed(self):
        return self._genericProtocol__fixed

    @fixed.setter
    def fixed(self, boolean):
        self._genericProtocol__fixed = boolean # pylint: disable=assigning-non-slot

    @qBaseSim.superSys.setter # pylint: disable=no-member
    def superSys(self, supSys):
        qBaseSim.superSys.fset(self, supSys) # pylint: disable=no-member
        supSys._qBase__paramBound[self.name] = self # pylint: disable=protected-access

    @property
    def unitary(self):
        if self._qUniversal__matrix is not None: # pylint: disable=no-member
            if ((self.fixed is True) or (self._paramUpdated is False)):
                unitary = self._qUniversal__matrix # pylint: disable=no-member
            else:
                unitary = self.getUnitary() # pylint: disable=assignment-from-no-return
                self._qBase__paramUpdated = False  # pylint: disable=assigning-non-slot
        else:
            self._qBase__paramUpdated = False  # pylint: disable=assigning-non-slot
            unitary = self.getUnitary() # pylint: disable=assignment-from-no-return
        return unitary

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
            self._qBase__paramBound[step.name] = step # pylint: disable=no-member
            if step._genericProtocol__inProtocol:
                super().addSubSys(copyStep(step))
            else:
                super().addSubSys(step)
                step._genericProtocol__inProtocol = True
                if step.superSys is None:
                    raise ValueError('?')

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
        self._qUniversal__matrix = unitary # pylint: disable=assigning-non-slot
        return unitary

    def prepare(self):
        for step in self.steps.values():
            if not isinstance(step, copyStep):
                step.prepare(self)


class Step(genericProtocol):
    instances = 0
    label = 'Step'
    __slots__ = ['__ratio', '__updates']
    def __init__(self, **kwargs):
        super().__init__(name=kwargs.pop('name', None))
        self.__ratio = 1
        self.__updates = []
        self._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member

    def prepare(self):
        if self.fixed is True:
            self.getUnitary()

    @property
    def system(self):
        return self.superSys

    @system.setter
    def system(self, supSys):
        genericProtocol.superSys.fset(self, supSys) # pylint: disable=no-member

    @property
    def updates(self):
        return self._Step__updates

    @property
    def ratio(self):
        return self._Step__ratio

    @ratio.setter
    def ratio(self, val):
        self._Step__ratio = val # pylint: disable=assigning-non-slot

    def _runCreateUnitary(self):
        for update in self._Step__updates:
            update.setup()
        unitary = self.createUnitary() # pylint: disable=assignment-from-no-return
        for update in self._Step__updates:
            update.setback()
        return unitary

    def getUnitary(self):
        super().getUnitary()
        if self.fixed is True:
            if self._qUniversal__matrix is None: # pylint: disable=no-member
                self._runCreateUnitary()
            self._qBase__paramUpdated = False # pylint: disable=assigning-non-slot
            unitary = self._qUniversal__matrix # pylint: disable=no-member
        elif ((self._paramUpdated is False) and (self._qUniversal__matrix is not None)): # pylint: disable=no-member
            unitary = self._qUniversal__matrix # pylint: disable=no-member
        else:
            self._qBase__paramUpdated = False # pylint: disable=assigning-non-slot
            unitary = self._runCreateUnitary()
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
        return self.superSys.unitary

class freeEvolution(Step):
    instances = 0
    label = 'freeEvolution'
    __slots__ = []
    def __init__(self, **kwargs):
        super().__init__(name=kwargs.pop('name', None))
        self._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member

    def createUnitary(self):
        super().createUnitary()
        unitary = lio.LiouvillianExp(2 * np.pi * self.superSys.totalHam, # pylint: disable=no-member
                                     timeStep=((self.simulation.stepSize*self.ratio)/self.simulation.samples))
        self._qUniversal__matrix = unitary # pylint: disable=assigning-non-slot
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
