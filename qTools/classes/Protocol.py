import qTools.QuantumToolbox.liouvillian as lio
import numpy as np
# import scipy.sparse as sp
# import qTools.QuantumToolbox.states as qSt
# from qTools.classes.QSys import QuantumSystem
# from qTools.classes.QUni import qUniversal
# from functools import partial
# from qTools.classes.exceptions import sweepInitError
""" under construction """


class Protocol:
    def __init__(self):
        self.steps = []

    def add_step(self, qSystem=None, key=None, time=0, value=None):
        step = Step(qSystem=None, key=None, time=0, value=None)
        self.steps.append(step)
        step.superSys = self.superSys
        return step

    def unitary(self):
        unitary = self.steps[0].unitary
        for step in self.steps[1:]:
            unitary = unitary @ self.step.unitary
        return unitary


class Step:
    def __init__(self, qSystem, key, time=0, value=None):
        self.qSystem = qSystem
        self.key = key
        self.value = value
        self.time = time

    def unitary(self):
        memory = getattr(self.qSystem, self.key)
        setattr(self.qSystem, self.key, self.value)
        unitary = lio.Liouvillian(
            2 * np.pi * self.superSys.totalHam, timeStep=self.time)
        setattr(self.qSystem, self.key, memory)
        return unitary
