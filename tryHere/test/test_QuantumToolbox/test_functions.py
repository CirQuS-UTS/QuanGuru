"""
Testing QuantumToolbox by comparing it with Qutip
"""

import qutip as qtp
import QuantumToolbox.functions as qt
import numpy as np

############################################################################################################
"""dimension = 4

state0 = (qtp.basis(dimension,3) + qtp.basis(dimension, 2)).unit()
state0.ptrace()
state1 = (qtp.basis(dimension,2) + qtp.basis(dimension, 0)).unit()
denMat0 = (state0 * state0.dag())
denMat1 = (state1 * state1.dag())
operator = qtp.num(dimension)

stateq0 = state0.data
denMatq0 = denMat0.data
stateq1 = state1.data
denMatq1 = denMat1.data
operatorq = operator.data

states0 = (stateq0).toarray()
denMats0 = (denMatq0).toarray()
states1 = (stateq1).toarray()
denMats1 = (denMatq1).toarray()
operators = (operatorq).toarray()"""

###################################
"""n = qtp.expect(operator,state0)
nq = qt.expectationKet(operatorq,stateq0)
ns = qt.expectationKet(operators,states0)
nd = qtp.expect(operator,denMat0)
nqd = qt.expectationKet(operatorq,denMatq0, ket=False)
nsd = qt.expectationKet(operators,denMats0, ket=False)

print(n, nq, ns)
print(nd, nqd, nsd)

n = qtp.expect(operator,state1)
nq = qt.expectationKet(operatorq,stateq1)
ns = qt.expectationKet(operators,states1)
nd = qtp.expect(operator,denMat1)
nqd = qt.expectationKet(operatorq,denMatq1, ket=False)
nsd = qt.expectationKet(operators,denMats1, ket=False)

print(n, nq, ns)
print(nd, nqd, nsd)"""

###################################
"""n = qtp.fidelity(state1,state1)
nq = qt.fidelity(stateq1,stateq1)
ns = qt.fidelity(states1,states1)
nd = qtp.fidelity(denMat1,denMat1)
nqd = qt.fidelity(denMatq1,denMatq1, ket=False)
nsd = qt.fidelity(denMats1,denMats1,ket=False)

print(n, nq, ns)
print(nd, nqd, nsd)

n = qtp.fidelity(state1,state0)
nq = qt.fidelity(stateq1,stateq0)
ns = qt.fidelity(states1,states0)
nd = qtp.fidelity(denMat1,denMat0)
nqd = qt.fidelity(denMatq1,denMatq0,ket=False)
nsd = qt.fidelity(denMats1,denMats0,ket=False)

print(n, nq, ns)
print(nd, nqd, nsd)"""

###################################
#print(np.log(dimension), np.log2(dimension))
"""state0 = (0.5*(qtp.basis(dimension,2) * qtp.basis(dimension,2).dag()) + 0.5*(qtp.basis(dimension, 3)*qtp.basis(dimension,3).dag()))
stateq0 = state0.data
states0 = (stateq0).toarray()

state1 = (0.5*(qtp.basis(dimension,2)*qtp.basis(dimension,2).dag()) 
          + 0.3*(qtp.basis(dimension, 0)*qtp.basis(dimension, 0).dag()) 
          + 0.2*(qtp.basis(dimension, 1)*qtp.basis(dimension, 1).dag()))
stateq1 = state1.data
states1 = (stateq1).toarray()"""

"""n0 = qtp.entropy_vn(state0)
n1 = qtp.entropy_vn(state1)
nq0 = qt.entropy(stateq0)
nq1 = qt.entropy(stateq1)
ns0 = qt.entropy(states0)
ns1 = qt.entropy(states1)

print(n0, nq0, ns0)
print(n1, nq1, ns1)

n0 = qtp.entropy_vn(state0,base=2)
n1 = qtp.entropy_vn(state1,base=2)
nq0 = qt.entropy(stateq0,base2=True)
nq1 = qt.entropy(stateq1,base2=True)
ns0 = qt.entropy(states0,base2=True)
ns1 = qt.entropy(states1,base2=True)

print(n0, nq0, ns0)
print(n1, nq1, ns1)"""

###################################
"""dims = [2,2,4]

state0 = qtp.basis(dims[0],0)
state1 = qtp.basis(dims[1],0)
state2 = qtp.basis(dims[2],0)

state = (qtp.tensor(qtp.tensor(state0,state1),state2)).unit()
#state = state * state.dag()
stateq = state.data
print(stateq)
states = stateq.toarray()

keep = [0,2]

n = (state.ptrace(keep)).data
nq = qt.partial_trace(stateq,keep,dims)
ns = qt.partial_trace(states,keep,dims)
print(n-nq)
print(n-ns)"""