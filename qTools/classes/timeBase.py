"""
    This module contain timeBase class, which has 3 basic time information required in time evolutions and an optional
    one.
"""

from qTools.classes.computeBase import stateBase, _parameter
# pylint: disable = cyclic-import

class timeBase(stateBase):
    """
    This base class contain 3 basis time information, namely total time of simulation (``totalTime``), step size for
    each unitary (``stepSize``), and number of steps (``stepCount = totalTime/stepSize``). Additionally, one more
    parameter, namely, number of samples
    (``samples``) is introduced to be used with time-dependent Hamiltonians, where a continuous parameter
    is discretely changed at every ``stepSize`` and more than one ``samples`` are desired during the ``stepSize``.

    These 4 attributes are all :class:`_parameter <qTools.classes.computeBase._parameter>` objects and private
    attributes, so they are modified by the corresponding properties (names here are property names). One other use of
    property is to create flexible use of these attributes. For example, not all 3 of ``stepSize``, ``totalTime``, and
    ``stepCount`` are need to be explicitly defined, any of these two would be sufficient, since the 3rd can be
    calculated using the two. So, property setters&getters also covers such cases. Another flexibility ensured by the
    properties is when ``_bound`` are broken.

    Attribute names and these explanations are enough to understand the basics for these 4 paramaters of timeBase class.
    See below for more details on the corresponding properties.
    """

    #: Total number of instances of the class
    instances: int = 0

    #: Used in default naming of objects. See :attr:`label <qTools.classes.QUni.qUniversal.label>`.
    label = 'timeBase'

    __slots__ = ['__totalTime', '__stepSize', '__samples', '__stepCount', '__bound']

    def __init__(self, **kwargs):
        super().__init__(_internal=kwargs.pop('_internal', False))
        self.__totalTime = _parameter()
        self.__stepSize = _parameter()
        self.__samples = _parameter(1)
        self.__stepCount = _parameter()
        self.__bound = None

        self._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member

    def save(self):
        """
        This method extends the :meth:`save <qTools.classes.QUni.qUniversal.save>` of :class:`qUniversal`. This one uses
        an alternative approach to :attr:`toBeSaved <qTools.classes.QUni.qUniversal.toBeSaved>` list, which is defining
        the list inside the function as opposed to being a class attribute. There are advantages and disadvantages for
        both approaches, but these methods are temporary anyway.
        """

        keys = ['stepSize', 'totalTime', 'samples', 'stepCount']
        try:
            saveDict = super().save()
        except TypeError:
            saveDict = {}

        if self.superSys is not None:
            saveDict['superSys'] = self.superSys.name # pylint: disable=no-member

        for key in keys:
            saveDict[key] = getattr(self, key)
        return saveDict

    @property
    def totalTime(self):
        """
        The totalTime property:

        - **getter** : ``returns _timeBase__totalTime.value``.
        - **setter** : sets ``_timeBase__totalTime.value``, and also ``_timeBase__stepCount.value`` conditioned on that
          ``stepSize`` is not ``None``. It also sets
          :meth:`_paramUpdated <qTools.classes.computeBase.paramBoundBase._paramUpdated>` to ``True``. Additionally to
          these, it sets ``_timeBase__stepSize._value`` to ``_timeBase__stepSize._bound._value``, if
          ``_timeBase__stepSize._bound`` is not ``None or False``. This is introduced to provide a flexible
          use of these parameters, such as not forcing to define at least 2 of 3 timeBase parameters, if it already
          has a ``_bound`` and can obtain the second one from the ``_bound``.
        """

        return self._timeBase__totalTime.value

    @totalTime.setter
    def totalTime(self, fTime):
        self._paramUpdated = True
        if self._timeBase__stepSize._bound not in (None, False):# pylint: disable=protected-access
            self._timeBase__stepSize._value = self._timeBase__stepSize._bound._value # pylint: disable=protected-access
        self._timeBase__totalTime.value = fTime # pylint: disable=assigning-non-slot
        if self.stepSize is not None:
            self._timeBase__stepCount.value = int((fTime//self.stepSize) + 1) # pylint: disable=assigning-non-slot

    @property
    def stepCount(self):
        """
        The stepCount property:

        - **getter** : ``returns _timeBase__stepCount.value`` but also sets ``totalTime`` if it is ``None``.
        - **setter** : sets ``_timeBase__stepCount.value`` and also ``_timeBase__stepSize.value`` conditioned on that
          ``totalTime`` is not ``None``. It also sets
          :meth:`_paramUpdated <qTools.classes.computeBase.paramBoundBase._paramUpdated>` to ``True``. Additionally to
          these, it sets ``_timeBase__totalTime._value`` to ``_timeBase__totalTime._bound._value``, if
          ``_timeBase__totalTime._bound`` is not ``None or False``. This is introduced to provide a flexible
          use of these parameters, such as not forcing to define at least 2 of 3 timeBase parameters, if it already
          has a ``_bound`` and can obtain the second one from the ``_bound``.
        """

        if self.totalTime is None:
            self._timeBase__totalTime.value = self._timeBase__stepCount.value * self.stepSize # pylint: disable=E0237
        self._timeBase__stepCount.value = int((self.totalTime//self.stepSize) + 1) # pylint: disable=assigning-non-slot
        return self._timeBase__stepCount.value

    @stepCount.setter
    def stepCount(self, num):
        self._paramUpdated = True
        if self._timeBase__totalTime._bound not in (None, False):# pylint: disable=protected-access
            self._timeBase__totalTime._value = self._timeBase__totalTime._bound._value# pylint: disable=protected-access
        self._timeBase__stepCount.value = num # pylint: disable=assigning-non-slot
        if self.totalTime is not None:
            self._timeBase__stepSize.value = self.totalTime/num # pylint: disable=assigning-non-slot

    @property
    def stepSize(self):
        """
        The stepSize property:

        - **getter** : ``returns _timeBase__stepSize.value``.
        - **setter** : sets ``_timeBase__stepSize.value`` and also ``_timeBase__stepCount.value`` conditioned on that
          ``totalTime`` is not ``None``. It also sets
          :meth:`_paramUpdated <qTools.classes.computeBase.paramBoundBase._paramUpdated>` to ``True``. Additionally to
          these, it sets ``_timeBase__totalTime._value`` to ``_timeBase__totalTime._bound._value``, if
          ``_timeBase__totalTime._bound`` is not ``None or False``. This is introduced to provide a flexible
          use of these parameters, such as not forcing to define at least 2 of 3 timeBase parameters, if it already
          has a ``_bound`` and can obtain the second one from the ``_bound``.
        """

        return self._timeBase__stepSize.value

    @stepSize.setter
    def stepSize(self, stepsize):
        self._paramUpdated = True
        if self._timeBase__totalTime._bound not in (None, False):# pylint: disable=protected-access
            self._timeBase__totalTime._value = self._timeBase__totalTime._bound._value# pylint: disable=protected-access
        self._timeBase__stepSize.value = stepsize # pylint: disable=assigning-non-slot
        if self.totalTime is not None:
            self._timeBase__stepCount.value = int((self.totalTime//stepsize) + 1) # pylint: disable=assigning-non-slot

    @property
    def samples(self):
        """
        The samples property:

        - **getter** : ``returns _timeBase__samples.value``.
        - **setter** : sets ``_timeBase__samples.value`` and also
          :meth:`_paramUpdated <qTools.classes.computeBase.paramBoundBase._paramUpdated>` to ``True``.
        """

        return self._timeBase__samples.value

    @samples.setter
    def samples(self, num):
        self._paramUpdated = True
        self._timeBase__samples.value = num # pylint: disable=assigning-non-slot

    def _bound(self, other, # pylint: disable=dangerous-default-value
               params=['_stateBase__delStates', '_stateBase__initialState', '_stateBase__initialStateInput'],
               re=False):
        """
        This method is used internally at appropriate places to create bound between different simulation instances in
        the intended hierarchical order. Meaning, when a :class:`quantum system <qTools.classes.QSys.genericQSys>` is
        added to ``subSys`` of explicitly created :class:`Simulation <qTools.classes.Simulation.Simulation>`.
        The parameters of any :class:`protocol.simulation <qTools.classes.QPro.genericProtocol>` for that system will
        be bound to ``(quantum system).simulation`` which will be bound to explicitly created Simulation. This method
        creates such a bound between two ``Simulation`` objects, and it is used in appropriate places of the library.
        Such a bound is broken or not created at all, if a parameter is explicitly assigned for a protocol or system.

        NOTE : This method is intended purely for internal uses!

        Parameters
        ----------
        other : Simulation
            The other Simulation (or timeBase) class to bound the parameters of self
        re : bool, optional
            This boolean used (internally) to **re-bound** a simulation object to another one, by default False. So,
            re-calling this method to bound a simulation object to another will not work unless ``re=True``.
        param: List[str]
            This is a list of strings for attributes (which are also _parameter objects) other than time parameters, for
            which the same bound will be created. The difference between ``param`` and ``timeBase`` parameters is that
            the latter ones has a functional dependency to each other, meaning a break in one of them should
            appropriately be reflected to the others.


        :returns: None
        """

        self._timeBase__bound = other # pylint: disable=assigning-non-slot
        keys = ['_timeBase__stepSize', '_timeBase__totalTime', '_timeBase__stepCount']
        keysProp = ['stepSize', 'totalTime', 'stepCount']
        bounding = True
        for ind, key in enumerate(keys):
            if getattr(self, key)._bound is False: # pylint: disable=protected-access
                if getattr(other, key)._value is not None: # pylint: disable=protected-access
                    setattr(self, keysProp[ind], getattr(self, key)._value) # pylint: disable=protected-access

                if bounding:
                    for i, k in enumerate(keys):
                        if ((getattr(self, k)._bound is None) and # pylint: disable=protected-access
                                (getattr(other, k)._value is not None)): # pylint: disable=protected-access
                            setattr(self, keysProp[i], getattr(other, k)._value) # pylint: disable=protected-access
                            break
                    bounding = False

        for key in (*keys, *params, '_timeBase__samples'):
            try:
                if ((getattr(self, key)._bound is None) or re): # pylint: disable=protected-access
                    if getattr(other, key)._bound in (None, False): # pylint: disable=protected-access
                        getattr(self, key)._bound = getattr(other, key) # pylint: disable=protected-access
                    elif isinstance(getattr(other, key)._bound, _parameter): # pylint: disable=protected-access
                        getattr(self, key)._bound = getattr(other, key)._bound # pylint: disable=protected-access
            except AttributeError:
                print('not bounding', key)
