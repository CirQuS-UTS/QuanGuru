import qTools.QuantumToolbox.liouvillian as lio
import numpy as np
# import scipy.sparse as sp
# import qTools.QuantumToolbox.states as qSt
# from qTools.classes.QSys import QuantumSystem
from qTools.classes.QUni import qUniversal
# from functools import partial
# from qTools.classes.exceptions import sweepInitError
""" under construction """


class __Protocol(qUniversal):
    def __init__(self, qSys, **kwargs):
        super().__init__(**kwargs)
        self.qSys = qSys
        self._qUniversal__setKwargs(**kwargs)


class Protocol(__Protocol):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.steps = []
        # maybe 

    def add_step(self, step):
        self.steps.append(step)

    @property
    def unitary(self):
        # need to find a way of not calculating this everytime it is called
        # (this is solved by the way time evolution functions)
        unitary = self.steps[0].unitary
        for step in self.steps[1:]:
            unitary = unitary @ self.step.unitary
        return unitary


class FreeEvolution(__Protocol):
    def __init__(self, qSys, time, **kwargs):
        super().__init__(qSys, **kwargs)
        self.time = time

    @property
    def unitary(self):
        unitary = lio.Liouvillian(2 * np.pi * self.qSys.totalHam,
                                  timeStep=self.time)
        return unitary


class Gate(__Protocol):
    pass
