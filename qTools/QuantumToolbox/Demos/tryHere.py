# import qTools.QuantumToolbox.states as qStates

# ket =qStates.basis()

'''from multiprocessing import Pool
import datetime
import time

def squareX(x):
    #time.sleep(x/1000)
    return x*x

if __name__ == '__main__':
    p = Pool(processes=4)
    listOfVals = [i for i in range(100)]

    t0 = datetime.datetime.now()
    resMap0 = p.map(squareX, listOfVals)
    t1 = datetime.datetime.now()
    resMap1 = p.map_async(squareX, listOfVals)
    resMap1 = resMap1.get()
    t2 = datetime.datetime.now()
    resMap2 = [p.apply(squareX, (value,)) for value in listOfVals]
    t3 = datetime.datetime.now()
    resMap3 = [p.apply_async(squareX, (value,)) for value in listOfVals]
    resMap3 = [ar.get() for ar in resMap3]
    t4 = datetime.datetime.now()

    print(t1-t0)
    print(t2-t1)
    print(t3-t2)
    print(t4-t3)

    print(resMap0 == resMap1)
    print(resMap2 == resMap3)
    print(resMap2 == resMap0)

    print(resMap0)
    print(resMap1)
    print(resMap2)
    print(resMap3)'''
