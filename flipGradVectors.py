#!/usr/bin/env python
# Author: David Qixiang Chen
# email: qixiang.chen@gmail.com
#
# Flip signs of a particular gradient vector dimension

from optparse import OptionParser
import os
import sys
import numpy as np
import pynrrd as nrrd

def run(options, args):
	infile = args[0]
	outfile = args[1]

	flip_file(infile, outfile, axis=options.axis, dryrun=options.dryrun)

def flip_file(infile, outfile, axis='1', dryrun=False):
	ax = [ int(i) for i in axis.split(',') ]	

	if infile.endswith('.nrrd') or infile.endswith('.nhdr'):
		header, data = nrrd.NrrdReader().load(infile)
		dvecs = header._data['DWMRI_gradient']
		dvecs = np.asarray(dvecs)
	else:
		dvecs = np.loadtxt(infile)

	print '=========== Before ============='
	print dvecs[:20]

	dvecs = flip_vecs(dvecs, ax)
	print '=========== After ============='	
	print dvecs[:20]

	if not dryrun:
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
    parser.add_option("-a", "--axis", dest="axis", default='1', help="Axis to invert, comma-separated, default is 1 (Y)")
    parser.add_option("-n", "--dry-run", action='store_true',dest="dryrun", help="Dry run, don't save output",default=False)
    options, args =  parser.parse_args()

    if len(args) < 2:
        parser.print_help()
        sys.exit(2)

    else:
        run(options, args)
