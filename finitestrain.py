#!/usr/bin/python
import numpy as np
import sys

def winvhalf(X):
    """    
    equivalent to matlab code M^-0.5
    """
    e, V = np.linalg.eigh(X)
    return np.dot(V, np.dot(np.linalg.inv(np.diag(e+0j)**0.5),V.T))

def correct_bvecs(bvecs, data):
    """
    Perform finite strain correction for bvecs
    """
    if bvecs.shape[1] > bvecs.shape[0]:
        bvecs = bvecs.T

    cor_bvecs = np.zeros(bvecs.shape)

    trans = np.split(data, bvecs.shape[0])
    for i, bvec in enumerate(bvecs):
        rt = np.matrix(trans[i][:3,:3], dtype=np.complex)
        R = np.real(winvhalf(rt*rt.T)*rt)
        cor_bvecs[i] = np.nan_to_num(bvec*R.T)
    return cor_bvecs

if __name__ == '__main__':
    fname = sys.argv[1]
    bvecs_file = sys.argv[2]
    out_file = sys.argv[3]

    data = np.loadtxt(fname)
    bvecs = np.loadtxt(bvecs_file)

    cor_bvecs = correct_bvecs(bvecs, data)

    print cor_bvecs
    np.savetxt(out_file, cor_bvecs, fmt='%.10f')
    