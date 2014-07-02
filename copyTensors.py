#!/usr/bin/python

# Author: David Qixiang Chen
# email: qixiang.chen@gmail.com
#
# Copy tensors from a tensor volume to fiber tracks

from optparse import OptionParser
import numpy, math
import nrrd
import sys
import os
import gzip
from StringIO import StringIO

options = []
args = []
fiberfile = []
is_tensor = False

def run():
    global options,args,is_tensor

    header, tensors = openTensorData()
    params = header._data
    points = openFiberFile()


    voxeldir = params['space directions']
    if params['kinds'][0] == '3D-symmetric-matrix':
        print 'VALUES IS 3D-SYMMETRIC-MATRIX. CANNOT PROCEED. PLEASE RESAVE FILE'
        return

    if params['kinds'][0] == '3D-matrix':
        # first space dir is none, so skip
        voxeldir = voxeldir[1:]
        is_tensor = True

    print voxeldir

    # get voxel dimensions
    vdim = [0,0,0]
    for i in range(3):
        d = numpy.array(voxeldir[i])
        # easy way to get the voxel dimension by computing the magitude of space direction vector
        vdim[i] = float(numpy.sqrt(numpy.dot(d,d)))


    vspacemat = numpy.matrix(voxeldir)
    vspacemat = vspacemat.T

    print 'volume matrix: ',vspacemat
    vspace_inv = vspacemat.I

    dirs = [1,1,1]
    origin= params['space origin']
    print 'origin: ',origin

    print '------------------- tensor info -----------------------'
    #tensors = numpy.swapaxes(tensors,0,3)

    print '# shape: ',tensors.shape

    pointTensors = []
    #p = points[0]
    idx = []

    for p in points:
        index = getVolumeIndex(p, origin, vspace_inv, dirs)
        idx.append(index)
        tensormat = tensors[index[2],index[1],index[1]]
        #tensormat = numpy.array(tensors[index[2]][index[1]][index[0]])

        if is_tensor:
            tensormat = tensormat.reshape([3,3])
        print tensormat
        #tensormat = tensormat * vspacemat
        pointTensors.append(list(numpy.ravel(tensormat)))

    writeFiber(pointTensors, header)
    idx = numpy.array(idx)
    print '# min corner= ',numpy.amin(idx,axis=0)
    print '# max corner= ',numpy.amax(idx,axis=0)


##
# Docs: http://www.vtk.org/VTK/img/file-formats.pdf
# VTK point_data tyep def is of format:
#   SCALARS dataName dataType numComp
def writeFiber(pointTensors, header):
    global options, fiberfile
    print '# write fiber file: ',options.output
    outfile = open(options.output, 'w')
    for l in fiberfile:
        outfile.write(l)
    outfile.write('\n')
    outfile.write('POINT_DATA %d\n' % len(pointTensors))
    if is_tensor:
        outfile.write('TENSORS tensors float\n')
    else:
        outfile.write('FIELD FieldData 1\n')
        outfile.write('FA 1 %d float\n' % len(pointTensors))

    for i in pointTensors:
#            print '\r',
#            for j in i:
#                print j,
        if is_tensor:
            outfile.write('%f %f %f %f %f %f %f %f %f\n' % (i[0],i[1],i[2],i[3],i[4],i[5],i[6],i[7],i[8]))
        else:
            outfile.write('%f\n' % (i[0]))

    print '\n'
    outfile.close()


def indexCoordinate(index, origin, vmat, dirs):
    index = numpy.array(index)
    origin = numpy.array(origin)
    point =  index * vmat
    return numpy.ravel(numpy.asarray(point))+origin

# get the ijk volume index based on xyz world point coordinate
def getVolumeIndex(point, origin, vmat, dirs):
    point = numpy.array(point)
    origin = numpy.array(origin)

    print '#xyz= ',point,

    # adjust for origin offeset
    point = point - origin

    # apply inverse transform
    vpoint =  point * vmat

    # adjust to ijk index (0 start), and convert to int
    vpoint = vpoint - 1
    vpoint = numpy.ravel(numpy.asarray(vpoint, dtype=numpy.int))
    print '  #ijk= ',vpoint

    return vpoint

def openFiberFile():
    global options
    global fiberfile
    filename = options.fiber
    file = open(filename,'r')
    numpoints = 0
    points = []
    readpoint = False
    lcount = 0
    while file:
        line = file.readline()
        fiberfile.append(line)
        if len(line) == 0:
            break
        line = line.strip()
        if line.startswith('POINTS'):
            vals = line.split(' ')
            numpoints = int(vals[1])
            readpoint = True
            lcount = 0
        elif readpoint:
            if lcount < numpoints:
                vals = line.split(' ')
                for i in range(len(vals)):
                    vals[i] = float(vals[i])
                points.append(vals)
                lcount+=1
            else:
                readpoint = False
    file.close()
    return points




def openTensorData():
    header, bindata = openTensorFile()
    params = header._data
    for k in params.keys():
        print k + ': ',
        print params[k]

    if bindata is None:
        FILE = params['data file'][0]
        print FILE
    encoding = params['encoding'][0]
    sizes = params['sizes']
    sizes.reverse()

    data = numpy.array([])
    # cast volume into datatype
    datatype = numpy.float32


    if encoding == 'gzip':
        if bindata is None:
            f = gzip.open(FILE, 'r')
            bindata = f.read()
            f.close()
        else:
            bindata = gzip.GzipFile(fileobj=StringIO(bindata)).read()
        data = numpy.fromstring(bindata, dtype=datatype)
    elif encoding == 'raw':
        if bindata is None:
            data = numpy.fromfile(file=FILE, dtype=datatype)
        else:
            data = numpy.fromstring(bindata, dtype=datatype)

    data.resize(sizes)
    return header, data

def openTensorFile():
    global options
    reader = nrrd.NrrdReader()
    header, data = reader.getFileAsHeader(options.tensor)
    return header, data




if __name__ == '__main__':
    parser = OptionParser(usage="Usage: %prog -i input")
    parser.add_option("-t", "--tensor", dest="tensor",help="Input tensor volume file")
    parser.add_option("-f", "--fiber", dest="fiber",help="Input vtk fiber file")
    parser.add_option("-o", "--output", dest="output",help="Ouput vtk file")

    (options, args) =  parser.parse_args()

    if not options.tensor:
        parser.print_help()
        sys.exit(2)
    else:
        run()
