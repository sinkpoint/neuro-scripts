#!/usr/bin/python
# Author: David Qixiang Chen
# email: qixiang.chen@gmail.com
#
# Flip signs of a particular gradient vector dimension

from optparse import OptionParser
import os
import sys
import numpy as np
import nrrd

def run(options, args):
	if not options.axis:
		axis = [1]
	else :
		axis = [ int(i) for i in options.axis.split(',') ]

	infile = args[0]
	outfile = args[1]

	flip_file(infile, outfile, indices=axis)

def flip_file(infile, outfile, indices=[1]):

	if infile.endswith('.nrrd') or infile.endswith('.nhdr'):
		header, data = nrrd.NrrdReader().getFileAsHeader(infile)
		dvecs = header._data['DWMRI_gradient']
	else:
		dvecs = np.loadtxt(infile)

	print '=========== Before ============='
	print dvecs[:20]

	dvecs = flip_vecs(dvecs, indices)
	print '=========== After ============='	
	print dvecs[:20]

	if not options.dryrun:
		if infile.endswith('.nrrd') or infile.endswith('.nhdr'):
			header._data['DWMRI_gradient'] = dvecs
			nrrd.NrrdWriter().write(header, outfile)
		else:
			np.savetxt(outfile, dvecs, fmt='%10.6f')


def flip_vecs(dvecs, idims):
	for i in idims:
		dvecs[:,i] *= -1

	return dvecs


if __name__ == '__main__':
    parser = OptionParser(usage="Usage: %prog [options] <input> <output>")
    parser.add_option("-a", "--axis", dest="axis",help="Axis to invert, comma-separated, default is 1 (Y)")
    parser.add_option("-n", "--dry-run", action='store_true',dest="dryrun", help="Dry run, don't save output",default=False)
    options, args =  parser.parse_args()

    if len(args) < 2:
        parser.print_help()
        sys.exit(2)

    else:
        run(options, args)
