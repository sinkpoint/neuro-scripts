#!/usr/bin/env python
import numpy as np

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

    print '-- before --'
    print bvecs

    cor_bvecs = np.zeros(bvecs.shape)

    trans = np.split(data, bvecs.shape[0])
    for i, bvec in enumerate(bvecs):
        rt = np.matrix(trans[i][:3,:3], dtype=np.complex)
        R = np.real(winvhalf(rt*rt.T)*rt)
        cor_bvecs[i] = np.nan_to_num(bvec*R.T)
    return cor_bvecs

if __name__ == '__main__':
    from optparse import OptionParser
    import sys
    parser = OptionParser(usage="Usage: %prog [options]")
    parser.add_option("-t", "--transforms", dest="trans", help="Resulting N4 transforms as ascii text")
    parser.add_option("-i", "--in", dest="in_file", help="Input bvecs file", )
    parser.add_option("-o", "--out", dest="out_file", help="Output file")
    parser.add_option("-f", "--is_fsl", action="store_true", dest="is_fsl", help="Transform file is a fsl ecclog file")

    (options, args) = parser.parse_args()
    if not options.in_file or not options.out_file or not options.trans:
        parser.print_help()
        sys.exit(2)

    fname = options.trans
    bvecs_file = options.in_file
    out_file = options.out_file

    if options.is_fsl:
        def filter_gen(f):
            for l in f:
                l = l.strip()
                if l and not l[0].isalpha():
                    yield l
        with open(fname) as f:
            data = np.genfromtxt(filter_gen(f))
            data = np.vstack((np.eye(4),data))
    else:
        data = np.loadtxt(fname)
    bvecs = np.loadtxt(bvecs_file)
    cor_bvecs = correct_bvecs(bvecs, data)

    print '-- after --'
    print cor_bvecs
    np.savetxt(out_file, cor_bvecs, fmt='%.10f')
