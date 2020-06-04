"""
    This module contains the updateBase class, which is inherited by :class:`_sweep <qTools.classes.Sweep._sweep>` and
    :class:`Update <qTools.classes.QPro.Update>` classes.
"""

from qTools.classes.QUni import qUniversal

class updateBase(qUniversal):
    """
    This class has only two attributes, which are private attributes intended to be used with different properties in
    the ``_sweep`` and ``Update`` classes to enable different terminologies for the same functionality.

    Attributes
    ----------
    key or _updateBase__key or __key : str
        This string value is the name of an attribute for the objects in ``subSys`` dictionary of an instance of
        updateBase, and the value of that attribute is updated by **an update function**.
    _updateBase__function or __function : Callable or None
        This is the aforementioned **update function**. This is not completely implemented in ``Update`` class, but the
        ``_sweep`` class, which will also be updated, has its basic use, which is pointing it to a default method to be
        used in updating the relevant attributes. The goal of making this an attribute is to enable user defined
        functions to be used, if some form of customisation is needed. TODO : cross-reference this to fixed sample-rate
        for varying-step-size demos.
    """
    #: Total number of instances of the class
    instances: int = 0

    #: Used in default naming of objects. See :attr:`label <qTools.classes.QUni.qUniversal.label>`.
    label = 'updateBase'

    #: a list of str (attribute names) to be used with save method, it extends
    #: :attr:`toBeSaved <qTools.classes.QUni.qUniversal.toBeSaved>` list.
    toBeSaved = qUniversal.toBeSaved.extendedCopy(['key'])

    __slots__ = ['__key', '__function', '_aux']

    def __init__(self, **kwargs):
        super().__init__()

        self.__key = None
        self.__function = None
        self._aux = False

        self._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member

    def save(self):
        """
        This method extends the :meth:`save <qTools.classes.QUni.qUniversal.save>` of :class:`qUniversal` by using the
        extended :attr:`toBeSaved <qTools.classes.QUni.qUniversal.toBeSaved>` list and also collecting some of the
        information under a single key.
        """

        saveDict = super().save()
        sysDict = []
        for sys in self.subSys.values():
            sysDict.append(sys.name)
        saveDict['systems'] = sysDict
        return saveDict

    @property
    def key(self):
        """
        The key property:

        - **getter** : ``returns _updateBase__key``
        - **setter** : sets ``_updateBase__key`` string
        - **type** : ``str``
        """

        return self._updateBase__key

    @key.setter
    def key(self, keyStr):
        self._updateBase__key = keyStr # pylint: disable=assigning-non-slot

    @property
    def system(self):
        """
        The system property wraps ``subSys`` dictionary to create new terminology, it basically:

        - **getter** : ``returns subSys[0]`` if there is only one item in it, else ``returns list(subSys.values())``.
        - **setter** : works exactly as :meth:`subSys <qTools.classes.QUni.qUniversal.subSys>` setter.
        """

        qSys = list(self.subSys.values())
        return qSys if len(qSys) > 1 else qSys[0]

    @system.setter
    def system(self, qSys):
        super().addSubSys(qSys)

    def _runUpdate(self, val):
        """
        This simple method sets the attribute (for the given key) of every ``subSys`` to a given value (``val``). It
        returns ``None``.
        """

        for subSys in self.subSys.values():
            try:
                setattr(subSys, self._updateBase__key, val)
            except AttributeError as attrErr:
                if self._aux is True:
                    subSys.aux[self._updateBase__key] = val
                else:
                    raise attrErr
