import classes.QSys as qsys
import classes.QSim as qsim
import QuantumToolbox as qtbox
import QuantumToolbox.operators as oper
import scipy.sparse as sp
import QuantumToolbox.states as states
from functools import partial
from multiprocessing import Pool, cpu_count
import QuantumToolbox.functions as qFncs
import QuantumToolbox.operators as qOps
import matplotlib.pyplot as plt
import numpy as np
import QuantumToolbox.liouvillian as lio
import Plotting.Functions as pltFncs

print(qtbox.operators.create(2).A)
print(qtbox.operators.sigmaz().A)

resonatorDimension = 200
"""
HamiltonianCavity = sp.kron(oper.number(resonatorDimension),oper.identity(2), format='csc')
HamiltonianQubit = sp.kron(oper.identity(resonatorDimension),oper.sigmaz(), format='csc')
couplingHamiltonian = (sp.kron(oper.create(resonatorDimension), oper.sigmax(), format='csc')
                               + sp.kron(oper.destroy(resonatorDimension), oper.sigmax(), format='csc'))"""
g = 1.79
qfreq = 0
resFreq = 2

RabiSys = qsys.QuantumSystem()
JCSys = qsys.QuantumSystem()

cav1 = qsys.Cavity(dimension=resonatorDimension, frequency=resFreq)
cav2 = qsys.Cavity(dimension=resonatorDimension, frequency=resFreq)
RabiSys.addSubSys(cav1)
JCSys.addSubSys(cav2)

qub1 = RabiSys.createSubSys(subClass=qsys.Qubit,frequency=qfreq)
qub2 = JCSys.createSubSys(subClass=qsys.Qubit,frequency=qfreq)
"""print(qub1.frequency)



print(cav1.frequency)
print(cav1.dimension)"""
RabiSys.addCoupling([qub1,cav1],[qtbox.operators.sigmax, qtbox.operators.create], g)
JCSys.addCoupling([qub2,cav2],[qtbox.operators.destroy, qtbox.operators.create], g)
RabiSys.addCoupling([cav1, qub1],[qtbox.operators.destroy, qtbox.operators.sigmax], g)
JCSys.addCoupling([cav2, qub2],[qtbox.operators.destroy, qtbox.operators.create], g)
"""print(RabiSys.freeHam)
print(RabiSys.freeHam)
hamO = RabiSys.totalHam
hamO1 = RabiSys.totalHam
hamD = (resFreq*HamiltonianCavity) + (qfreq*HamiltonianQubit) + (g*couplingHamiltonian)
print(hamO.A)
print(hamD.A)
print(hamD - hamO)
print((hamD - hamO).A)"""
RabiSys.initialState = sp.kron(states.basis(cav1.dimension, 0), states.basis(2, 1), format='csc')
JCSys.initialState = sp.kron(states.basis(cav1.dimension, 0), states.basis(2, 1), format='csc')

def digitalRabi(obj, stepSize):
    HamJC = 2 * np.pi * (((obj.subSystems[0].frequency/2)*obj.subSystems[0].freeMat()) + obj.couplingHam)
    UnitaryJC = lio.Liouvillian(HamJC, timeStep=(stepSize / 2))
    UnitaryAJC = (UnitaryJC @ UnitaryJC)
    Unitary = UnitaryJC @ obj.sigmaX @ UnitaryAJC @ obj.sigmaX @ UnitaryJC
    return Unitary

JCSys.sigmaX = sp.kron(oper.identity(cav2.dimension), oper.sigmax())
JCSys.Unitaries = digitalRabi

qSim = qsim.Simulation(RabiSys)
qSimDig = qsim.Simulation(JCSys)
qSim.sweepKey = 'frequency'
qSimDig.sweepKey = 'frequency'

cavParity = qOps.parityEXP(cav1.freeMat())
p = Pool(processes=cpu_count())
print('simulating Ideal')
statesIdeal = p.map(partial(qSim.evolveTimeIndep, cav1), qSim.sweepList)
parityIdeal = p.map(partial(qFncs.expectationList, cavParity),statesIdeal)
print('simulating digital')
statesDigit = p.map(partial(qSimDig.evolveTimeIndep, cav2), qSim.sweepList)
parityDigit = p.map(partial(qFncs.expectationList, cavParity),statesDigit)

cm = plt.get_cmap('inferno')
fig, ax = plt.subplots()
Y, X = np.meshgrid(qSim.times, qSim.sweepList)
surf1 = ax.pcolormesh(X, Y, parityIdeal,cmap=cm,norm=pltFncs.normalizeCMAP(cm, -1, 1))

fig2, ax2 = plt.subplots()
Y, X = np.meshgrid(qSim.times, qSim.sweepList)
surf2 = ax2.pcolormesh(X, Y, parityDigit,cmap=cm,norm=pltFncs.normalizeCMAP(cm, -1, 1))
plt.show()