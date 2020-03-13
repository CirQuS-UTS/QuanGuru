class Update(qUniversal):
    instances = 0
    label = 'Update'
    slots = ['system', 'key', 'value', '__memory']
    def __init__ (self, **kwargs):
        super().__init__()
        self.system = None
        self.key = None
        self.value = None
        self.__memory = None
        self._qUniversal__setKwargs(**kwargs)

    def setup(self):
        self._Update__memory = getattr(self.system, self.key)
        setattr(self.system, self.key, self.value)
    
    def setback(self):
        setattr(self.system, self.key, self._Update__memory)