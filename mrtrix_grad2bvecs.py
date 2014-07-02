#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Tue May 13 13:28:11 2014

@author: dchen
"""

import sys
import os
import numpy as np

mhelp="""
Usage: %s <mrtrix_grad_file>

This program converts mrtrix gradient files that is generated from mrinfo -g to fsl compatible bvec and bval files.
"""

if len(sys.argv) < 2:
    print mhelp
    sys.exit()

fin=sys.argv[1]
basename = os.path.splitext(fin)[0]


m = np.loadtxt(fin)
g = m[:,0:3]
v = m[:,3]

np.savetxt(basename+'.bvec', g, fmt='%.6f')
np.savetxt(basename+'.bval', v, fmt='%d')

