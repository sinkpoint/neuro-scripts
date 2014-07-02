import numpy as np
import nibabel as nib
import vtk
import argparse
from multiprocessing import Pool

_DEBUG = 0



def run(args):

    ref_image = nib.load(args.ref)
    imgdim = ref_image.get_shape()[:3]
    outData = np.zeros(imgdim)
    outBinData = np.zeros(imgdim)
    outFibData = np.zeros(imgdim)

    outbasename = args.out.split('.')[0]

    streamlines = vtkToStreamlines(args.in_fiber)
    points = np.concatenate(streamlines)

    #points = np.array([[100,100,20,1],[101,101,21,1]])
    pones = np.ones([points.shape[0],1])

    #stream_bounds = np.matrix(bounding_box(points))
    #stream_bounds =  np.vstack((stream_bounds,[1,1])).T

    rheader = ref_image.get_header()
    ijk2rasMx = np.matrix(rheader.get_best_affine())

    ras2ijkMx = ijk2rasMx.I

    #points = (points * ijk2rasMx.T)[:,:3]
    #st_ijk_bounds = np.int_(stream_bounds * ras2ijkMx.T)
    pt_ijk = np.int_(np.append(points, pones, axis=1) * ras2ijkMx.T)

    # get unique voxel index for tract mask

    b = np.ascontiguousarray(pt_ijk).view(np.dtype((np.void, pt_ijk.dtype.itemsize * pt_ijk.shape[1])))
    pt_ijk = np.unique(b).view(pt_ijk.dtype).reshape(-1, pt_ijk.shape[1])
    pt_ijk3 = pt_ijk[:,:3]
    print pt_ijk3


    outBinData[pt_ijk3[:,0],pt_ijk3[:,1],pt_ijk3[:,2]] = 1

    # output binary tract mask
    outImage = nib.Nifti1Image( outBinData, ref_image.get_affine() )
    nib.save(outImage, outbasename+'_bin.nii.gz')


    for i in pt_ijk3:
        vals = getIjkDensity(streamlines, ref_image, i) * 100
        outData[i[0],i[1],i[2]] = vals[0]
        outFibData[i[0],i[1],i[2]] = vals[1]

    outImage = nib.Nifti1Image( outData, ref_image.get_affine() )
    nib.save(outImage, args.out)

    outFibImage = nib.Nifti1Image(outFibData, ref_image.get_affine())
    nib.save(outFibImage, outbasename+'_fib.nii.gz')

    return

def myrange(i,j):
    if i>j:
        return range(j,i)
    else:
        return range(i,j)

def vtkToStreamlines(filename):
    vreader = vtk.vtkPolyDataReader()
    vreader.SetFileName(filename)
    vreader.Update()
    inputPolyData = vreader.GetOutput()

    streamlines = []
    for i in range(inputPolyData.GetNumberOfCells()):
        pts = inputPolyData.GetCell(i).GetPoints()
        npts = np.array([pts.GetPoint(i) for i in range(pts.GetNumberOfPoints())])
        streamlines.append(npts)
    return streamlines

def bounding_box(nparray):
    """
    Find max and min values given a Nx3 numpy array
    nparray -- Nx3 numpy array
    Returns [(min_x, max_x), (min_y, max_y), (min_z, max_z)]
    """
    min_x, min_y, min_z = nparray.min(axis=0)
    max_x, max_y, max_z = nparray.max(axis=0)

    return (min_x, max_x), (min_y, max_y), (min_z, max_z)

def getIjkDensity(streamlines, ref_image, index):
    """
    docs
    """

    rheader = ref_image.get_header()
    ijk2rasMx = rheader.get_best_affine()

    # get voxel center in RAS
    ijkvec = np.matrix(np.append(index,1))

    voxel_ras = ijkvec * ijk2rasMx.T
    voxel_ras = np.array(voxel_ras).flatten()[:3]
    # get the bounds of voxel

    shape = rheader.get_zooms()[:3]
    minCorner = voxel_ras - shape
    maxCorner = voxel_ras + shape


    vox_density, num_fiber = getDensityOfBounds(streamlines, minCorner, maxCorner)

    print index, vox_density, num_fiber
    return vox_density, num_fiber


def getDensityOfBounds( streamlines, minCornerRAS, maxCornerRAS):
    num_pass = 0
    for line in streamlines:
        if np.any(np.all(line <= maxCornerRAS, axis=1)) and np.any(np.all(line>= minCornerRAS, axis=1)):
            num_pass+=1
#            print num_pass,'pass!'

#        continue
#        for point in line:
#            print point
#            print point < maxCornerRAS,point > minCornerRAS
#            if np.all(point < maxCornerRAS) and np.all(point > minCornerRAS):
#                print point
#                num_pass += 1
#                continue

    numFibers = len(streamlines)
    density = float(num_pass)/float(numFibers)

    return density, num_pass


def fibers_from_vtkPolyData(streamlines, minCorner, maxCorner, minimumFiberLength=1):
        #Fibers and Lines are the same thing
        # fiber refers to a list of actual points that make up the fiber
        # line refers to the indexs into the points array that makes up the line

        # GetLines return vtkCelArray type, which list data as (n, id1, id2,...,idn, n, id1, id2,...idn,...) format
        lines = vtkPolyData.GetLines().GetData().ToArray().squeeze()
        points = vtkPolyData.GetPoints().GetData().ToArray()

        fibersList = []
        linesList = []
        actualLineIndex = 0
        newpointsIndex = 0
        newpoints = []
        newlines = []

        numberOfFibers = len(streamlines)

        for l in xrange( numberOfFibers ):
            linelen = lines[actualLineIndex]
            if linelen > minimumFiberLength:
                fiber = points[ lines[actualLineIndex+1: actualLineIndex+linelen+1] ]
                passfiber = []
                newline = []
                for point in fiber:
                    inrange = True
                    for i in range(3):
                        if ( point[i] < minCorner[i] or point[i] > maxCorner[i]):
                            inrange = False
                            break
                    if inrange is True:
                        passfiber.append(point)
                        newpoints.append(point)
                        newline.append(len(newpoints)-1)
                if len(passfiber) > 0:
                    fibersList.append( passfiber )
                    newlines.append(len(passfiber))
                    newlines.extend(newline)
                #linesList.append( lines[actualLineIndex+1: actualLineIndex+linelen+1]    )
            actualLineIndex += linelen+1

        return fibersList, newpoints, newlines

def debug( msg ):
    global _DEBUG
    if _DEBUG:
        print msg

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Converts vtk tracts to nifti density image")
    parser.add_argument("-f", "--in_fiber", required=True, dest="in_fiber",help="Input fiber bundle in vtk")
    parser.add_argument("-m", "--mask", dest="mask",help="Integer binary mask")
    parser.add_argument("-r", "--reference", dest="ref",help="Reference image to use as image space")
    parser.add_argument("-s", "--resolution", dest="res",help="If no reference image, then the resolution of voxel, default=1")
    parser.add_argument("-o", "--output", dest="out",help="Output nifti filename")

    args =  parser.parse_args()

    run(args)