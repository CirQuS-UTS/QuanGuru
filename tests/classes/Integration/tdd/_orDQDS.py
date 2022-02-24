import quanguru as qg
import numpy as np


# some default parameters
cavityDimension = 50
spinNumber = 0.5
couplingStrength = 1
spinFrequency = 3.5
cavityFrequency = 3.5

# objects for digital
cavityDigital = qg.Cavity(dimension=cavityDimension, frequency=cavityFrequency/2, alias='cavityDigital')
spinDigital = qg.Spin(frequency=spinFrequency, jValue=spinNumber, alias='spinDigital')
digitalSystem = cavityDigital + spinDigital
digitalCoupling = digitalSystem.JC(couplingStrength/np.sqrt(2*spinNumber))
digitalSystem.initialState = [0,0]

# objects for Dicke
cavityDicke = qg.Cavity(dimension=cavityDimension, frequency=cavityFrequency, alias='cavityDicke')
spinDicke = qg.Spin(frequency=spinFrequency, jValue=spinNumber, alias='spinDicke')
ds = cavityDicke + spinDicke
# NOTE use of Jx in coupling vs Jp + Jm lead to factor of 2
DickeCoupling = ds.Dicke((2*couplingStrength)/np.sqrt(2*spinNumber))
ds.initialState = [0,0]

# digital protocol
unitaryStep = qg.freeEvolution(ratio=0.5, superSys=digitalSystem)

bitFlip1 = qg.SpinRotation(system=spinDigital, phase=1, rotationAxis='x', angle=np.pi)
bitFlip2 = qg.SpinRotation(system=spinDigital, phase=-1, rotationAxis='x', angle=np.pi)

antiUnitary = qg.freeEvolution(superSys=digitalSystem)
spinFrequencyUpdate = antiUnitary.createUpdate(system=spinDigital, key='frequency', value=0)
antiUnitaryStep = qg.qProtocol(steps=[bitFlip1, antiUnitary, bitFlip2])

dd = qg.qProtocol(superSys=digitalSystem, steps=[unitaryStep, antiUnitaryStep, unitaryStep], alias='dd')

# simulation object
simulation = qg.Simulation(subSys=ds)
simulation.addSubSys(digitalSystem, dd)

spinValues = [0.5, 6]

couplingValues1 = [couplingStrength/np.sqrt(2*spinValue) for spinValue in spinValues]
couplingValues2 = [(2*couplingStrength)/np.sqrt(2*spinValue) for spinValue in spinValues]

cavityDimensions = [int(np.round(cavityDimension*(2*j + 1)/(13))) for j in spinValues]

stepSizesDicke = [0.01, 0.125]

jvaluesDigit = simulation.Sweep.createSweep(system=spinDigital, sweepKey='jValue', sweepList=spinValues)
jvaluesDicke = simulation.Sweep.createSweep(system=spinDicke, sweepKey='jValue', sweepList=spinValues)

gvaluesDigit = simulation.Sweep.createSweep(system=digitalCoupling, sweepKey='frequency', sweepList=couplingValues1)
gvaluesDicke = simulation.Sweep.createSweep(system=DickeCoupling, sweepKey='frequency', sweepList=couplingValues2)

cavDimSizeSweepDigit = simulation.Sweep.createSweep(system=cavityDigital, sweepKey='dimension', sweepList=cavityDimensions)
cavDimSizeSweepDicke = simulation.Sweep.createSweep(system=cavityDicke, sweepKey='dimension', sweepList=cavityDimensions)

stepSizeSweep = simulation.Sweep.createSweep(system=simulation, sweepKey='stepSize', sweepList=stepSizesDicke, multiParam=True)

def calcEigStat(op, ob):
    valsProtoc, vecsProtoc = qg.eigenVecVal._eigs(op)
    componentsEigS = qg.eigenVecVal._eigStatEig(vecsProtoc, symp=True)
    ob.qRes.result = ['vecStat', componentsEigS]
    return valsProtoc, vecsProtoc

def calculateDig(protoc):
    calcEigStat(protoc.unitary(), protoc)
dd.calculateStart = calculateDig

def calculateIde(sys):
    #calcEigStat(sys.totalHam, sys)
    calcEigStat(sys.totalHamiltonian, sys)
ds.calculateStart = calculateIde

simulation.auxDict['totalDim'] = -1
def calculateOps(sim):
    cav = sim.getByNameOrAlias('cavityDigital')
    qub = sim.getByNameOrAlias('spinDigital')
    totalDim = sim.qSystems[0].dimension
    if sim.auxDict['totalDim'] != totalDim:
        sim.auxDict['totalDim'] = totalDim
        #sim.auxDict['cavPhoton'] = cav.freeMat
        sim.auxDict['cavPhoton'] = cav._freeMatrix
simulation.calculateStart = calculateOps

def compute(qsim, args):
    cavPhoton = qsim.auxDict['cavPhoton']
    stateDicke = args[0]
    stateDigit = args[1]
    qsim.qRes.result = ['nIde', qg.expectation(cavPhoton, stateDicke)]
    qsim.qRes.result = ['nDig', qg.expectation(cavPhoton, stateDigit)]
    qsim.qRes.result = ['sfid', qg.fidelityPure(stateDicke, stateDigit)]
simulation.compute = compute

simulation.totalTime = 0.8
simulation.delStates = True
