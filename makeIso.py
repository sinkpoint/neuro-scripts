#!/usr/bin/python
import nibabel as nib
from optparse import OptionParser
from dipy.align.reslice import reslice
import sys

def makeIso(filename, outname, voxel_size=1.):
    img = nib.load(filename)
    data = img.get_data()
    zooms = img.get_header().get_zooms()[:3]
    affine = img.get_affine()

    # reslice image into 1x1x1 iso voxel

    new_zooms = (voxel_size, voxel_size, voxel_size)
    data2, affine2 = reslice(data, affine, zooms, new_zooms)
    img = nib.Nifti1Image(data2, affine2)

    print data2.shape
    print img.get_header().get_zooms()
    print "###"

    nib.save(img, outname)

if __name__ == '__main__':
    parser = OptionParser(usage="Usage: %prog input output")

    (options, args) =  parser.parse_args()

    if len(args)<2:
        parser.print_help()
        sys.exit(2)
    else:
        makeIso(args[0],args[1])