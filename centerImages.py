#!/usr/bin/python
# -*- coding: utf-8 -*-

from optparse import OptionParser
import nibabel as nib
import nibabel.nifti1 as nutils
import numpy as np
import os.path
import sys

def run(options, args):
    filename=args[0]
    output = args[1]
    outfolder = os.path.dirname(output)


    basefilename = os.path.basename(output)
    root,ext = os.path.splitext(basefilename)
    if ext in ['.gz']:
        tok = os.path.splitext(root)
        root = tok[0]
        ext = tok[1] + ext

    print "output to",output

    img = nib.loadsave.load(filename)

    affine = np.matrix(img.get_header().get_best_affine())
    shape = np.array(img.shape)
    zooms = np.array(img.get_header().get_zooms())
    real_dim = shape * zooms

    is_apply_matrix = False
    if options.matrix:
        is_apply_matrix = True
        output = outfolder + root + ext
        trans = np.matrix(np.loadtxt(options.matrix))
    else:
        output = outfolder + root + "_centered" + ext
        invert_trans_file = outfolder + root + "_inv.txt"

        trans = np.matrix(np.identity(4))
        trans[0,3] = affine[0,3] * -1
        trans[1,3] = affine[1,3] * -1
        trans[2,3] = affine[2,3] * -1

    new_affine = trans * affine


    nimg = nutils.Nifti1Image(img.get_data(), new_affine, img.get_header())
    nib.loadsave.save(nimg, output)

    if not is_apply_matrix:
        np.savetxt(invert_trans_file,trans.I)

if __name__ == '__main__':
    parser = OptionParser(usage="Usage: %prog <flags> input output")
    parser.add_option("-m", "--matrix", dest="matrix",help="Apply this transformation matrix to the input instead. Useful for apply inverse matrices.")

    (options, args) =  parser.parse_args()

    if len(args) < 2:
        parser.print_help()
        sys.exit(2)
    else:
        run(options, args)