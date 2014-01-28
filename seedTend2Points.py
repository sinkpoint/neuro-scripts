#!/usr/bin/python

# Author: David Qixiang Chen
# email: qixiang.chen@gmail.com
# 
# Generates seed points for multi-tensor tractography in TEEM

from optparse import OptionParser
import gzip
import numpy
import os
import sys
from nrrd import NrrdReader

options = []
args = []

def run():
	global options,args
	
	nrrdr = NrrdReader()
	
	params = nrrdr.getFileContent(options.input)
	for k in params.keys():
		print k,' : ',params[k]
		
	dim = params['sizes']	
	dimX = dim[0]
	dimY = dim[1]
	dimZ = dim[2]
	
	numSeeds = 9
	seedThresh = numSeeds * 30
	radius = 0.5
	spacing = 0.3

	filename = params['data file'][0]
	f = gzip.open(filename, 'r')
	FILE = f.read()
	f.close()	
	

	datatype = numpy.short
	size = dimX*dimY*dimZ
	shape = (dimX, dimY, dimZ)
	data = numpy.fromstring(FILE, dtype=datatype)
	print data.shape
	print shape
	print shape[0]*shape[1]*shape[2]
	data = data.reshape(shape, order='F') #matlab uses fortran order; numpy uses c order
	

	if not os.path.isdir("seeds"):
		print 'make seeds dirs'
		os.mkdir("seeds")
	os.chdir("seeds")
	print os.getcwd()

	filemap = {}
	
	seedPoints = 0;
	fileCount = 1;
	for z in range(0, dimZ):
		for y in range(0, dimY):
			for x in range(0, dimX):
				val = data[x][y][z]
				if val > 0:
					if not filemap.has_key(val):
						filename = 'IC%d.txt' % val
						filemap[val] = open(filename, 'w')
					
					print '(%d,%d,%d) \t %d' % (x,y,z,data[x][y][z])
					vx = x
					vy = y
					vz = z
					
					for zz in numpy.arange(vz-radius,vz+radius,spacing):
						for yy in numpy.arange(vy-radius,vy+radius,spacing):
							for xx in numpy.arange(vx-radius,vx+radius,spacing):
								str = '%f %f %f\n' % (xx,yy,zz)								
								filemap[val].write(str)

					seedPoints = seedPoints + numSeeds;

#					if seedPoints % seedThresh == 0:
#						OUT.close()
#						fileCount += 1
#						newfile = 'IC%d.txt' % fileCount
#						OUT = open(newfile, 'w')
	for i in filemap.values():
			i.close()
	
	
		
	

if __name__ == '__main__':	
	parser = OptionParser(usage="Usage: %prog -i input")
	parser.add_option("-i", "--input", dest="input",help="Input file name")
	parser.add_option("-d", "--dim", dest="dim",help="Volume dimension", default="256,256,44")
	#parser.add_option("-o", "--output", dest="output", help="output file name")	
	(options, args) =  parser.parse_args()

	if not options.input:
		parser.print_help()
		sys.exit(2)
	else:
		run()
