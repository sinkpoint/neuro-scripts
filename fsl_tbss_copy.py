#!/usr/bin/env python

import os, sys, shlex
from glob import glob
from subprocess import call
from optparse import OptionParser

dirsNotFound = []
options = []
args = []

def goProc():
    global  dirsNotFound, options, args
    
    rootdir = os.getcwd()
    os.chdir(options.input)
    inputdir = os.getcwd()
    
    os.chdir(rootdir)
    os.chdir(options.output)
    outputdir = os.getcwd()
    
    for basedir in args:
        os.chdir(inputdir)
        if not os.path.isdir(basedir):
            # not a valid dir, skip
            dirsNotFound.append(basedir)
            continue
    
        os.chdir(basedir)
        absbasedir = os.getcwd()
        search = options.search        
        dirs = glob(search)
        print dirs
    
        for dti in dirs:
            os.chdir(absbasedir)
            os.chdir(dti)
            print os.getcwd()
             
            if os.path.isdir("nii"):
                for f in glob('nii/*_FA.nii.gz'):
                    cmd = 'cp %s %s' % (f, outputdir)
                    print cmd
                    call(shlex.split(cmd))
    
    if len(dirsNotFound) > 0:
        print "These dirs where not found: "
        for i in dirsNotFound:
            print i
    
if __name__ == '__main__':
    parser = OptionParser(usage="Usage: %prog [options] <subject_dir>")
    parser.add_option("-s", "--search", dest="search", default='*DTI*', metavar='STRING', help="DTI dir name to search for. i.e *DTI*")
    parser.add_option("-i", "--inputDir", dest="input", default='.', metavar='FILE', help="Input dir to start searching")
    parser.add_option("-o", "--outputDir", dest="output", default='.', metavar='FILE', help="Destination dir to copy files to")
    #parser.add_option("-d", "--dti_dir", dest="dir", help="Only process this directory, if set will ignore -s options and any arg supplied")
    #parser.add_option("-n", "--name", dest="name", help="Base subject name for beautifying output")

    (options, args) = parser.parse_args()

    if len(args) < 1:
        parser.print_help()
        sys.exit(2)
    else:
        goProc()