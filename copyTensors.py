#!/usr/bin/python

# Author: David Qixiang Chen
# email: qixiang.chen@gmail.com
# 
# Copy tensors from a tensor volume to fiber tracks

from optparse import OptionParser
import numpy, math
import sys
import os
import gzip

options = []
args = []
fiberfile = []

def run():
    global options,args
    
    params, tensors = openTensorData()
    points = openFiberFile()
    voxeldir = params['space directions'][1:]
    vdim = [0,0,0]
    for i in range(3):
        d = numpy.array(voxeldir[i])
        vdim[i] = float(numpy.sqrt(numpy.dot(d,d)))
    vspacemat = numpy.matrix(voxeldir)
    vspacemat = vspacemat.T
    vspace_inv = vspacemat.I
    
    dirs = [1,1,1]
    origin= params['space origin']
    
    

    pointTensors = []
    #p = points[0]
    for p in points:
        index = getVolumeIndex(p, origin, vspace_inv, dirs)
        tensormat = numpy.array(tensors[index[2]][index[1]][index[0]])
        #tensormat = tensormat.reshape([3,3])        
        #tensormat = tensormat * vspacemat 
        pointTensors.append(list(numpy.ravel(tensormat)))
    
    writeFiber(pointTensors)
        
        
def writeFiber(pointTensors):
    global options, fiberfile    
    outfile = open(options.output, 'w')
    for l in fiberfile:
        outfile.write(l)
    outfile.write('\n')
    outfile.write('POINT_DATA %d\n' % len(pointTensors))
    outfile.write('TENSORS tensors float\n')
    
    for i in pointTensors:
            print i
            outfile.write('%f %f %f %f %f %f %f %f %f\n' % (i[0],i[1],i[2],i[3],i[4],i[5],i[6],i[7],i[8]))
    
    outfile.close()
        

def indexCoordinate(index, origin, vmat, dirs):
    index = numpy.array(index)
    origin = numpy.array(origin)
    point =  index * vmat    
    return numpy.ravel(numpy.asarray(point))+origin

def getVolumeIndex(point, origin, vmat, dirs):
    point = numpy.array(point)
    origin = numpy.array(origin)
    point = point - origin    
    vpoint =  point * vmat
    return numpy.ravel(numpy.asarray(vpoint, dtype=numpy.int))      

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
    params = openTensorFile()
    for k in params.keys():
        print k + ': ',
        print params[k]
    
    file = params['data file']
    encoding = params['encoding'][0]
    sizes = params['sizes']
    sizes.reverse()
    
    data = numpy.array([])
    datatype = numpy.float32
    if encoding == 'gzip':
        f = gzip.open(file, 'r')
        content = f.read()
        f.close()
        data = numpy.fromstring(content, dtype=datatype)
    elif encoding == 'raw':
        data = numpy.fromfile(file=FILE, dtype=datatype)
    
    data.resize(sizes)
    return params, data
    
def openTensorFile():
    global options
    TFILE = open(options.tensor, 'r')
    params = {}

    while ( TFILE ):
        line = TFILE.readline()
        if len(line) == 0:
            break;
        line = line.strip()
        if line.startswith('#'):
            continue
        
        if line.startswith('NRRD'):
            params['header'] = line
        else:
            key,val = line.split(':')
            key = key.strip()
            val = val.strip()
            if key != 'data file':
                val = getVals(val)
            if key == 'sizes':
                for i in range(len(val)):
                    val[i] = int(val[i])
            params[key]= val
    TFILE.close()
    return params

def getVals(input):
    input = input.replace('(','')
    input = input.replace(')','')
    input = input.split(' ')
    res = []        
    for i in input:
        if ',' in i:
            i = i.split(',')
            for k in range(len(i)):
                i[k] = float(i[k])
        res.append(i)
    if len(res) == 1:
        a = numpy.array(res)
        res = list(numpy.ravel(a))
    return res


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
