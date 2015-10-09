#!/usr/bin/env python

# Author: David Qixiang Chen
# email: qixiang.chen@gmail.com
#
# Generates seed points for multi-tensor tractography in TEEM

from optparse import OptionParser
import gzip
import numpy
import os
import sys
from pynrrd import NrrdReader
from StringIO import StringIO

def run(options, args):
    seed_xst(options.input, name=options.name, spacing=options.spacing, num_points=options.num_points, is_rand=options.isRand)

def seed_xst(filename, name='IC', spacing=0.3, is_rand=True, num_points=10):
    nrrdr = NrrdReader()

    params, bindata = nrrdr.load(filename, get_raw=True)
    # for k in params.keys():
    #     print k,' : ',params[k]
    params = params._data
    dim = params['sizes']
    dimX = dim[0]
    dimY = dim[1]
    dimZ = dim[2]

    numSeeds = 9
    seedThresh = numSeeds * 30
    radius = 0.5

    datatype = numpy.uint8
    print params['type']
    if params['type'] == 'float':
        datatype = numpy.float32
    elif params['type'] == 'double':
        datatype = numpy.double 
    elif params['type'] == 'short':
        datatype = numpy.short

    size = dimX*dimY*dimZ
    shape = (dimX, dimY, dimZ)

    if 'data file' in params:
        filename = params['data file']
        f = gzip.open(filename, 'r')
        FILE = f.read()
        f.close()
    else:
        FILE=gzip.GzipFile(fileobj=StringIO(bindata)).read()

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
                        filename = name+'%d.txt' % val
                        filemap[val] = open(filename, 'w')

                    print '(%d,%d,%d) \t %d' % (x,y,z,data[x][y][z])
                    vx = x
                    vy = y
                    vz = z

                    if is_rand:
                        points = numpy.random.uniform(size=[num_points, 3]) + [vx-0.5, vy-0.5, vz-0.5]
                        for p in points:
                            str = '%f %f %f\n' % (p[0],p[1],p[2])
                            filemap[val].write(str)

                    else:
                        for zz in numpy.arange(vz-radius,vz+radius,spacing):
                            for yy in numpy.arange(vy-radius,vy+radius,spacing):
                                for xx in numpy.arange(vx-radius,vx+radius,spacing):
                                    str = '%f %f %f\n' % (xx,yy,zz)
                                    filemap[val].write(str)

                    seedPoints = seedPoints + numSeeds;

#                    if seedPoints % seedThresh == 0:
#                        OUT.close()
#                        fileCount += 1
#                        newfile = 'IC%d.txt' % fileCount
#                        OUT = open(newfile, 'w')
    for i in filemap.values():
            i.close()





if __name__ == '__main__':
    parser = OptionParser(usage="Usage: %prog -i input")
    parser.add_option("-i", "--input", dest="input",help="Input file name")
    parser.add_option("-s", "--spacing", dest="spacing", type="float", help="Seed spacing", default="0.3")
    parser.add_option("-r", "--random", action="store_true", dest="isRand")
    parser.add_option("-n", "--num_points", dest="num_points", type="int", default="10")
    parser.add_option("-m", "--name", dest="name", default="IC")
    #parser.add_option("-o", "--output", dest="output", help="output file name")
    (options, args) =  parser.parse_args()

    if not options.input:
        parser.print_help()
        sys.exit(2)
    else:
        run(options, args)
