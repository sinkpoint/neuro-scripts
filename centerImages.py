#!/usr/bin/python
# -*- coding: utf-8 -*-

import nibabel as nib
import nibabel.nifti1 as nutils
import numpy as np
import os.path
import sys

filename=sys.argv[1]
output = sys.argv[2]
outfolder = os.path.dirname(output)


basefilename = os.path.basename(output)
root,ext = os.path.splitext(basefilename)
if ext in ['.gz']:
    tok = os.path.splitext(root)
    root = tok[0]
    ext = tok[1] + ext


output = outfolder + root + "_centered" + ext
invert_trans_file = outfolder + root + "_inv.txt"

print "output to",output

img = nib.loadsave.load(filename)

affine = np.matrix(img.get_header().get_best_affine())
shape = np.array(img.shape)
zooms = np.array(img.get_header().get_zooms())
real_dim = shape * zooms

trans = np.matrix(np.identity(4))
trans[0,3] = affine[0,3] * -1
trans[1,3] = affine[1,3] * -1
trans[2,3] = affine[2,3] * -1

new_affine = trans * affine


nimg = nutils.Nifti1Image(img.get_data(), new_affine, img.get_header())
nib.loadsave.save(nimg, output)
np.savetxt(invert_trans_file,trans.I)
