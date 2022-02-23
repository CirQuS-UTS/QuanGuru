import quanguru as qg
import numpy as np

jValeu = 400

j_orthogonal = jValeu
p_orthogonal = 1
p_pert  = 0.001

u1COE = qg.Spin(operator=qg.Jy, frequency=p_orthogonal, jValue=j_orthogonal)
u2COE = qg.Spin(operator=qg.Jz, frequency=1, order=2, jValue=j_orthogonal)

kt = qg.qProtocol(superSys=u1COE, steps=[qg.freeEvolution(superSys=u1COE, ratio=1/(2*np.pi)), qg.freeEvolution(superSys=u2COE, ratio=1/(2*np.pi*2*j_orthogonal))])
kt.simStepSize = 1

kt.simTotalTime = 10
list(kt.steps.values())[0].simSamples = 10
kt.initialState = qg.states.basis(u1COE.dimension, 1)
kickStrength = [0.02, 2.15, 6.08, 5.74]
kt.simulation.Sweep.createSweep(system=u2COE, sweepKey='frequency', sweepList=kickStrength)
perturbed = qg.qProtocol(superSys=u2COE, steps=[*kt.steps.values(), qg.freeEvolution(superSys=u2COE, ratio=0.001/(2*np.pi*2*j_orthogonal), simStepSize=1)])
perturbed.initialState = kt.initialState
kt.simulation.addProtocol(perturbed)
jz = qg.Jz(jValeu)
def compute(qsim, states):
    p1 = qsim.qEvolutions[0]
    p2 = qsim.qEvolutions[1]
    for s in range(len(p1.sampleStates)):
        qsim.qRes.result = ['ex', qg.expectation(jz, p1.sampleStates[s])/jValeu]
        qsim.qRes.result = ['fd',qg.fidelityPure(p1.sampleStates[s], p2.sampleStates[s])]
        qsim.qRes.result = ('dl', qg.iprKetNB(p1.sampleStates[s])/((2*jValeu)+1))
kt.simCompute = compute
#kt.simulation.run(p=False)
