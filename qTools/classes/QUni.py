class qUniversal:
    instances = 0
    label = 'qUniversal'
    instNames = {}
    __slots__ = ['__name','__superSys', '__ind','__subSys']
    def __init__(self, **kwargs):
        super().__init__()
        self._incrementInstances()
        self.__name = self.__namer()
        self.__superSys = None
        self.__subSys = {}
        self.__ind = None
        self._qUniversal__setKwargs(**kwargs)

    def __del__(self):
        class_name = self.__class__.__name__
    
    def __setKwargs(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    @property
    def subSystems(self):
        return self._qUniversal__subSys

    @subSystems.setter
    def subSystems(self, subS):
        self._qUniversal__addSubSys(subS)
             
    def __addSubSys(self, subS):
        if isinstance(subS, qUniversal):
            self._qUniversal__subSys[subS.name] = subS
        elif isinstance(subS, str):
            self._qUniversal__addSubSys(self.instNames[subS])
        elif isinstance(subS, dict):
            for sys in subS.values():
                self._qUniversal__addSubSys(subS)
        else:
            for sys in subS:
                self._qUniversal__addSubSys(subS)
        return subS

    @property
    def superSys(self):
        return self._qUniversal__superSys

    @superSys.setter
    def superSys(self, supSys):
        self._qUniversal__superSys = supSys

    @property
    def ind(self):
        return self._qUniversal__ind

    @ind.setter
    def ind(self, numb):
        self._qUniversal__ind = numb

    @property
    def name(self):
        return self._qUniversal__name
        
    @name.setter
    def name(self, name):
        self._qUniversal__name = qUniversal.updateNames(self, name)

    @classmethod
    def updateNames(cls, obj, name):
        if name in cls.instNames.keys():
            if cls.instNames[name] is not obj:
                name += str(obj.__class__.instances)
                print('You have given a duplicate name,' + '\n' + 'it is changed to ' + name)
        cls.instNames[name] = obj
        return name

    @staticmethod
    def createCopy(qUninstance, **kwargs):
        sysClass = qUninstance.__class__
        newSub = sysClass(**kwargs)
        return newSub
        
    def __namer(self):
        name = self.clsLabel() + str(self.clsInstances())
        # TODO might uncomment this to make all the names available, currently only speacial names are available
        #qUniversal.instNames[name] = self
        return name

    @classmethod
    def _incrementInstances(cls):
        cls.instances += 1

    @classmethod
    def clsInstances(cls):
        return cls.instances

    @classmethod
    def clsLabel(cls):
        return cls.label
        