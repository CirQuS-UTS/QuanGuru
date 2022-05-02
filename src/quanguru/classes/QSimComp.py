r"""
    Contains the parent class of quantum systems and protocols.
    Every system and protocol has a simulation, and this class creates this composition.

    .. currentmodule:: quanguru.classes.QSimComp

    .. autosummary::

        QSimComp

    .. |c| unicode:: U+2705
    .. |x| unicode:: U+274C
    .. |w| unicode:: U+2000

    =======================    ==================    ================   ===============
       **Function Name**        **Docstrings**        **Unit Tests**     **Tutorials**
    =======================    ==================    ================   ===============
      `QSimComp`                 |w| |w| |w| |c|       |w| |w| |c|        |w| |w| |c|
    =======================    ==================    ================   ===============

"""
from .baseClasses import computeBase
from .QSim import Simulation # pylint: disable=import-outside-toplevel


class QSimComp(computeBase):
    r"""
    Inhereted by the :class:`quantum systems <quanguru.classes.QSys.genericQSys>` and
    :class:`protocols <quanguru.classes.QPro.genericProtocol>` and has a
    simulation attribute which is an instance of :class:`Simulation <quanguru.classes.Simulation.Simulation>`. The goal
    for such an attribute is to increase possible ways of running a
    :class:`Simulation <quanguru.classes.Simulation.Simulation>`.

    NOTE : This class branches the inheritance started by :class:`paramBoundBase`, and this branch extends to
    :class:`quantum systems <quanguru.classes.QSys.genericQSys>` and
    :class:`protocols <quanguru.classes.QPro.genericProtocol>`.
    """
    #: (**class attribute**) class label used in default naming
    label = 'QSimComp'
    #: (**class attribute**) number of instances created internally by the library
    _internalInstances: int = 0
    #: (**class attribute**) number of instances created explicitly by the user
    _externalInstances: int = 0
    #: (**class attribute**) number of total instances = _internalInstances + _externalInstances
    _instances: int = 0

    __slots__ = ['__simulation']

    def __init__(self, **kwargs) -> None:
        super().__init__(_internal=kwargs.pop('_internal', False))
        #: an instance of Simulation (as a protected attribute) to run
        # ``self.simulation.run`` without any explicit Simulation creation and/or ``subSys`` addition call.
        self.__simulation = Simulation(_internal=True, superSys=self)
        self._QSimComp__simulation._paramBoundBase__paramBound[self.name] = self # pylint: disable=protected-access
        self._named__setKwargs(**kwargs) # pylint: disable=no-member
        # self.__openSystem = False

    @property
    def simulation(self):
        r"""
        ``returns _QSimComp__simulation`` attribute (an instance of :class:`~Simulation`).
        """
        return self._QSimComp__simulation

    def runSimulation(self, p=None, coreCount=None):
        r"""
        an alternative to run the simulation, equivalent to ``self.simulation.run()``
        """
        return self._QSimComp__simulation.run(p=p, coreCount=coreCount)

    @property
    def _initialStateInput(self):
        return self.simulation._stateBase__initialStateInput.value

    @property
    def simParameters(self):
        r"""
        returns a tuple contaning simulation parameters for the self.simulation, which might be bound to some other
        simulation object and getting values from there.

        There are various setters of this property with different names to set the relevant attribute of the simulation.
        # TODO should we include calculate methods into the tuple ? and have a setter for calculates as well ?
        """
        return ('totalTime:', self.simulation.totalTime, 'stepSize:', self.simulation.stepSize, 'stepCount:',
                self.simulation.stepCount, 'samples:', self.simulation.samples, 'delStates:',
                self.simulation.delStates, 'compute:', self.simulation.compute)

    @simParameters.setter
    def simTotalTime(self, fTime):
        r"""
        setter for the totalTime of Simulation, equivalent to ``self.simulation.totalTime = fTime``
        """
        self.simulation.totalTime = fTime

    @simParameters.setter
    def simStepSize(self, stepsize):
        r"""
        setter for the stepSize of Simulation, equivalent to ``self.simulation.stepSize = stepsize``
        """
        self.simulation.stepSize = stepsize

    @simParameters.setter
    def simStepCount(self, num):
        r"""
        setter for the stepCount of Simulation, equivalent to ``self.simulation.stepCount = num``
        """
        self.simulation.stepCount = num

    @simParameters.setter
    def simSamples(self, num):
        r"""
        setter for the samples of Simulation, equivalent to ``self.simulation.samples = num``
        """
        self.simulation.samples = num

    @simParameters.setter
    def simCompute(self, func):
        r"""
        setter for the compute of Simulation, equivalent to ``self.simulation.compute = func``
        """
        self.simulation.compute = func

    @simParameters.setter
    def simDelStates(self, boolean):
        r"""
        setter for the delStates of Simulation, equivalent to ``self.simulation.delStates = boolean``
        """
        self.simulation.delStates = boolean

    @property
    def initialState(self):
        r"""
        Getter for the simulation initial state, equivalent to ``self.simulation.initialState``.
        This works by assuming that its setter/s makes sure that _stateBase__initialState.value is not None
        for single systems (if its state is set).
        """
        return self.simulation.initialState

    def delMatrices(self, _exclude=[]): # pylint: disable=dangerous-default-value
        r"""
        This method extends :meth:`delMatrices <paramBoundBase.delMatrices>` of :class:`computeBase` to also call
        :meth:`delMatrices <paramBoundBase.delMatrices>` on ``self.simulation``.
        """
        if self not in _exclude:
            _exclude = super().delMatrices(_exclude)
            _exclude = self.simulation.delMatrices(_exclude)
        return _exclude
