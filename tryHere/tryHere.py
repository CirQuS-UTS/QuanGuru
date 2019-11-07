from QuantumToolbox.Hamiltonians import cavQubFreeHam, RabiHam, JCHam, AJCHam
from classes.parameterObj import Model
from RabiModel.Modules.Hamiltonians import Hamiltonians
import scipy.sparse as sp
import QuantumToolbox.operators as oper


resonatorDimension = 2

HamiltonianCavity = sp.kron(oper.number(resonatorDimension),oper.identity(2), format='csc')
HamiltonianQubit = sp.kron(oper.identity(resonatorDimension),oper.sigmaz(), format='csc')
couplingHamiltonian = (sp.kron(oper.create(resonatorDimension), oper.sigmax(), format='csc')
                           + sp.kron(oper.destroy(resonatorDimension), oper.sigmax(), format='csc'))
couplingJC = (sp.kron(oper.create(resonatorDimension), oper.destroy(2), format='csc')
                  + sp.kron(oper.destroy(resonatorDimension), oper.create(2), format='csc'))
sigmaX = sp.kron(oper.identity(resonatorDimension),oper.sigmax(), format='csc')

hR = HamiltonianCavity + 0*HamiltonianQubit + couplingHamiltonian
hJC = 0.5*HamiltonianCavity + 0.5*HamiltonianQubit + couplingJC
hAJC = sigmaX @ hJC @ sigmaX

_, qubH = cavQubFreeHam(1,1,2)
rh = RabiHam(1,0,1,2)
jc = JCHam(0.5,0.5,1,2)
ajc = AJCHam(0.5,-0.5,1,2)

print(hR.toarray())
print(rh.toarray())
print((hJC+hAJC).toarray())
print((jc + ajc).toarray())

print("jc Ham")
print(hJC.toarray())
print(jc.toarray())
print("ajc Ham")
print(hAJC.toarray())
print(ajc.toarray())
