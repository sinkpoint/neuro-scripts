#!/usr/bin/python

import sys
import numpy as np
from optparse import OptionParser

def run(options, args):
	bvec = np.loadtxt(options.bvec)
	bval = np.loadtxt(options.bval)
	
	if bvec.shape[0] < bvec.shape[1]:
		bvec = bvec.transpose()
	
	grad = np.column_stack((bvec, bval))
	
	print "original"
	print grad
	# invert GE grad axis for mrtrix
	grad[:,0]	*=  -1
	
#	print grad[:,1]
	grad[:,1]	*=  -1	
	
	print "corrected"
	print "------------------------------"
	print grad
	
	np.savetxt(options.out, grad, fmt="%10.6f")
    
    
if __name__ == '__main__':
	parser = OptionParser(usage="Usage: %prog [options] <subject_dir>")
	parser.add_option("-v", "--bvec", dest="bvec")
	parser.add_option("-a", "--bval", dest="bval")
	parser.add_option("-o", "--out", dest="out", default="grad.txt")
	(options, args) = parser.parse_args()

	if not options.bvec or not options.bval :
		parser.print_help()
		sys.exit(2)
	else:
		run(options, args)
