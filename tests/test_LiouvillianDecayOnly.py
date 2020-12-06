import sys
sys.path.append('C:\\Users\\angsa\\Codes\\QuantumSimulations')
from qTools import *
from qTools import QuantumToolbox
import numpy as np

#Initial parameters
density = mat2Vec(np.array([[1, 0],[0, 0]]))    #Initial density matrix of an excited qubit
H = 0.5*sigmaz()                                #Hamiltonian of a qubit

rhoTestee = np.empty(shape=(100,100),dtype=complex)           # Empty arrays for the excited and ground state populations 
rhoTestgg = np.empty(shape=(100,100),dtype=complex)
rhoTesteg = np.empty(shape=(100,100),dtype=complex)           # Empty arrays for the excited and ground state populations 
rhoTestge = np.empty(shape=(100,100),dtype=complex)

rhoee = np.empty(shape=(100,100),dtype=complex)


#Generating Populations for different decay rate and time
stat = 0
for k in range(100):
    rhoTesteelist = []
    rhoTestgglist = []
    rhoTesteglist = []
    rhoTestgelist = []
    rhoeelist = []
    for t in range(100):
        stat = vec2Mat(LiouvillianExp(H, 300*t, [sigmam()], [0.00001*(k+1)])@density)
        rhoeelist.append(np.exp(-0.00001*(k+1)*300*t))
        rhoTesteelist.append(stat[0,0])
        rhoTestgglist.append(stat[1,1])
        rhoTesteglist.append(stat[0,1])
        rhoTestgelist.append(stat[1,0])
    
    rhoTestee[k]=rhoTesteelist
    rhoTestgg[k]=rhoTestgglist
    rhoTesteg[k]=rhoTesteglist
    rhoTestge[k]=rhoTestgelist
    rhoee[k]=rhoeelist

def test_willPass():
    
    assert (np.allclose(rhoTestee, rhoee)) is True # pylint: disable=comparison-with-itself
    assert (np.allclose(rhoTestgg, 1-rhoee)) is True









