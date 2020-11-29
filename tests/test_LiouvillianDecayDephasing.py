import sys
sys.path.append('C:\\Users\\angsa\\Codes\\QuantumSimulations')
from qTools import *
from qTools import QuantumToolbox
import numpy as np


#Initial parameters
density = mat2Vec(np.array([[0.5, 0.5],[0.5, 0.5]]))    #Initial density matrix of an excited qubit
H = 0.5*sigmaz()                                #Hamiltonian of a qubit

rhoTesteg = np.empty(shape=(100,100),dtype=complex)    #Empty arrays for the excited and ground state populations 
rhoTestge = np.empty(shape=(100,100),dtype=complex)

rhoeg = np.empty(shape=(100,100),dtype=complex)


#Generating Coherence terms for different decay rate and time
stat = 0
for k in range(100):
    rhoTesteglist = []
    rhoTestgelist = []
    rhoeglist = []
    for t in range(100):
        stat = vec2Mat(LiouvillianExp(H, 50*t, [sigmam()], [0.00001*(k+1)])@density)
        rhoeglist.append(0.5*np.exp(-(0.00001*(k+1)/2+1j)*50*t))
        rhoTesteglist.append(stat[0,1])
        rhoTestgelist.append(stat[1,0])
            
    rhoTesteg[k]=rhoTesteglist
    rhoTestge[k]=rhoTestgelist
    rhoeg[k]=rhoeglist


    def test_willPass():
        assert (np.allclose(rhoTesteg, rhoeg)) is True # pylint: disable=comparison-with-itself
    
    