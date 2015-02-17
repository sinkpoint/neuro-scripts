#!/usr/bin/python

import numpy as np
import nibabel as nib
from scipy.interpolate import *

def trilinear_interpolator_speedup( input_array, indices):
    """
        trilinear interpolation of a list of float indices into an input array
        @input input_array:(IxJxK array), incides:(Nx3 indices)
        output: (N,) list of values
    """    
    input_array = np.array(input_array)
    indices = np.array(indices)

    x_indices = indices[:,0]
    y_indices = indices[:,1]
    z_indices = indices[:,2]

    x0 = x_indices.astype(np.integer)
    y0 = y_indices.astype(np.integer)
    z0 = z_indices.astype(np.integer)
    x1 = x0 + 1
    y1 = y0 + 1
    z1 = z0 + 1

    # #Check if xyz1 is beyond array boundary:
    x1[np.where(x1==input_array.shape[0])] = x0.max()
    y1[np.where(y1==input_array.shape[1])] = y0.max()
    z1[np.where(z1==input_array.shape[2])] = z0.max()

    x = x_indices - x0
    y = y_indices - y0
    z = z_indices - z0

    #output = input_array[x0,y0,z0]
    #print output
    output = (input_array[x0,y0,z0]*(1-x)*(1-y)*(1-z) +
                 input_array[x1,y0,z0]*x*(1-y)*(1-z) +
                 input_array[x0,y1,z0]*(1-x)*y*(1-z) +
                 input_array[x0,y0,z1]*(1-x)*(1-y)*z +
                 input_array[x1,y0,z1]*x*(1-y)*z +
                 input_array[x0,y1,z1]*(1-x)*y*z +
                 input_array[x1,y1,z0]*x*y*(1-z) +
                 input_array[x1,y1,z1]*x*y*z)

    return output

def getVolumeIndex(point, origin, vmat, dirs):
    point = np.array(point)
    origin = np.array(origin)

    #print '#xyz= ',point,

    # adjust for origin offeset
    point = point - origin

    # apply inverse transform
    vpoint =  point * vmat

    # adjust to ijk index (0 start), and convert to int
    vpoint = vpoint - 1
    vpoint = np.ravel(np.asarray(vpoint))
    #print '  #ijk= ',vpoint

    return vpoint

def copyScalarsToVtk(nifti_img, vtk_file, output_file, scalar_name='Scalar'):
    img = nib.load(nifti_img)
    affine = np.matrix(img.get_affine())
    print affine
    img_data = img.get_data()

    ph_data = np.zeros(img_data.shape)
    dims = ph_data.shape
    for i,v in enumerate(np.linspace(0,10,num=dims[0])):
        ph_data[i] += v

    coords = []
    vals = []

    aff_inv = affine.I

    from vtkFileIO import vtkToStreamlines
    import vtk

    streams, vtkdata = vtkToStreamlines(vtk_file)
    points = np.concatenate(streams)
    print 'world'
    max = np.amax(points, axis=0)
    print max
    min = np.amin(points, axis=0)
    print min


    points = np.hstack((points,np.ones((points.shape[0],1))))
    #coords = np.hstack((coords,np.ones((coords.shape[0],1))))

    #coords_world = coords * affine
    points_ijk = aff_inv * points.T
    points_ijk = points_ijk.T[:,:3]

    print 'ijk'
    max = np.amax(points_ijk, axis=0)
    print max
    min = np.amin(points_ijk, axis=0)
    print min

    import time
    s = time.time()
    scalars = trilinear_interpolator_speedup(img_data, points_ijk)

    vtkScalars = vtk.vtkFloatArray()
    vtkScalars.SetName(scalar_name)
    vtkScalars.SetNumberOfComponents(1)
    #vtkScalars.SetNumberOfTuples(len(scalars))
    for i,v in enumerate(scalars):
        vtkScalars.InsertNextTuple1(v)
    vtkdata.GetPointData().SetScalars(vtkScalars)

    writer = vtk.vtkXMLPolyDataWriter()
    #writer = vtk.vtkPolyDataWriter()
    writer.SetInput(vtkdata)
    writer.SetFileName(output_file)
    writer.Write()

if __name__ == '__main__':
    import sys
    from optparse import OptionParser

    parser = OptionParser(usage="Usage: %prog -i input")
    parser.add_option("-m", "--input_image", dest="image",help="Input nifti volume file")
    parser.add_option("-i", "--fiber", dest="fiber",help="Input vtk fiber file")
    parser.add_option("-o", "--output", dest="output",help="Ouput vtk file")
    parser.add_option("-n", "--name", dest="name", default='Scalar', help="Name of the scalar to embed, default is 'Scalar'")

    (options, args) =  parser.parse_args()

    if not options.image or not options.fiber or not options.output:
        parser.print_help()
        sys.exit(2)
    else:
        copyScalarsToVtk(options.image, options.fiber, options.output, scalar_name=options.name)