from qTools.classes.QUni import qUniversal
import qTools.QuantumToolbox.liouvillian as lio

import numpy as np


class qDigital(qUniversal):
    instances = 0
    label = 'qDigital'
    __slots__ = []
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class TrotterStep(qUniversal):
    instances = 0
    label = 'TrotterStep'
    __slots__ = []
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class subStep(qUniversal):
    instances = 0
    label = 'subStep'
    __slots__ = ['fixed', 'type']
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fixed = False
        self.type = None


