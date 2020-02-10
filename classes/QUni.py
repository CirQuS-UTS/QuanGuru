class qUniversal:
    def __init__(self, **kwargs):
        super().__init__()
        self.__name = None
        self.__ind = None
        self.__setKwargs(**kwargs)


    def __del__(self):
        class_name = self.__class__.__name__
    
    def __setKwargs(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    @property
    def ind(self):
        return self.__ind

    @ind.setter
    def ind(self, numb):
        self.__ind = numb

    @property
    def name(self):
        return self._qUniversal__name if self._qUniversal__name is not None else self.ind
    @name.setter
    def name(self, name):
        self.__name = name
