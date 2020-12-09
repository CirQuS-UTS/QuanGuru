import numpy as np
from numpy.core.fromnumeric import diagonal

sigmaMinusReference = np.array([[0, 0], [1, 0]])
sigmaPlusReference = np.array([[0, 1], [0, 0]])

sigmaXReference = np.array([[0, 1], [1, 0]])
sigmaYReference = np.array([[0, -1j], [1j, 0]])
sigmaZReference = np.array([[1, 0], [0, -1]])
