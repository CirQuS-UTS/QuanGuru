import sys
sys.path.append('C:\\Users\\angsa\\Codes\\QuantumSimulations\\qTools')
import QuantumToolbox.evolution as evo
import numpy as np
from qTools import *

density = mat2Vec(np.array([[1, 0],[0, 0]]))    #Initial density matrix of an excited qubit
H = 0.5*sigmaz()                                #Hamiltonian of a qubit
rhoTestee = np.empty(shape=(10000,100))           # Empty arrays for the excited and ground state populations 
rhoTestg = np.empty(shape=(10000,100))
rhoee = np.empty(shape=(10000,100))


stat = 0
for k in range(10000):
    rhoTesteelist = []
    rhoTestgglist = []
    rhoeelist = []
    for t in range(100):
        stat = vec2Mat(LiouvillianExp(H, 0.01*t, [sigmam()], [0.00001*k])@density)
        rhoeelist.append(np.exp(-0.00001*k*0.01*t))
        rhoTesteelist.append(stat[0,0])
        rhoTestgglist.append(stat[1,1])
    
    rhoTestee[k]=rhoTesteelist
    rhoTestg[k]=rhoTestgglist
    rhoee[k]=rhoeelist
        

def test_willPass():    
    assert (np.allclose(rhoTestee, rhoee)) is True # pylint: disable=comparison-with-itself







