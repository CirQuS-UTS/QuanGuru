"""
Testing QuantumToolbox by comparing it with Qutip
"""

import qutip as qtp
import QuantumToolbox.liouvillian as qt
import scipy.sparse as sp

############################################################################################################
dimension = 4

Ham = qtp.num(dimension)
HamM = (Ham.data).tocsc()

collapseOps = [qtp.destroy(dimension)]
collapseOpsM = [(qtp.destroy(dimension).data).toarray()]
collapseOpsS = [(qtp.destroy(dimension).data).tocsc()]

################# Unitary #################
lioQT = qt.Liouvillian(HamM.toarray())
lioQTS = qt.Liouvillian(HamM)
lioQTP = (-1j * Ham).expm()

print(sp.isspmatrix(lioQT), sp.isspmatrix(lioQTS))
print('Exponential of Hamiltonian')
print(sp.csc_matrix(lioQT) - lioQTP.data)
print(lioQTS - lioQTP.data)

################# ME #################
lioQTme = qt.Liouvillian(HamM.toarray(), collapseOpsM, exp=False)
lioQTSme = qt.Liouvillian(HamM, collapseOpsS, exp=False)
lioQTPme = qtp.liouvillian(Ham,collapseOps)

print(sp.isspmatrix(lioQTme), sp.isspmatrix(lioQTSme))
print('Exponential of Liouvillian')
print(sp.csc_matrix(lioQTme) - lioQTPme.data)
print(lioQTSme - lioQTPme.data)

#print((sp.csc_matrix(lioQTme) - lioQTPme.data).toarray())