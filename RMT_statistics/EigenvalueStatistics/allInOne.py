from RMT_statistics.EigenvalueStatistics.DRabi import DRabi
from RMT_statistics.EigenvalueStatistics.HarmonicOscillator import HO
from RMT_statistics.EigenvalueStatistics.JC import JC
from RMT_statistics.EigenvalueStatistics.Rabi import Rabi
from SaveRead.saveH5 import saveData

dims = 2000

Harmonic = HO(2*dims)  # returns from ham and uni
JaynesCummings = JC(dims)  # returns from ham, uni, and analytical
QRabi = Rabi(dims)  # returns from ham, uni, and analytical
DQRabi = DRabi(dims)  # returns from uni

eigenvalues = {}
eigenvalues['HO EigVals from Ham'] = Harmonic[0]
print(len(Harmonic[0]))
eigenvalues['HO EigVals from Uni'] = Harmonic[1]
print(len(Harmonic[1]))
eigenvalues['JC EigVals from Ham'] = JaynesCummings[0]
print(len(JaynesCummings[0]))
eigenvalues['JC EigVals from Uni'] = JaynesCummings[1]
print(len(JaynesCummings[1]))
eigenvalues['JC EigVals from Ana'] = JaynesCummings[2][0:2*dims]
print(len(eigenvalues['JC EigVals from Ana']))
eigenvalues['Rabi EigVals from Ham'] = QRabi[0]
print(len(QRabi[0]))
eigenvalues['Rabi EigVals from Uni'] = QRabi[1]
print(len(QRabi[1]))
eigenvalues['Rabi EigVals from Ana'] = QRabi[2]
print(len(QRabi[2]))
eigenvalues['DRabi EigVals from Uni'] = DQRabi
print(len(DQRabi))
saveData(eigenvalues)


