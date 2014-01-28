#!/usr/bin/python

import os, sys, shlex
from glob import glob
from subprocess import call
from optparse import OptionParser

dirsNotFound = []
options = []
args = []


def dcm2nii(file):
    niis = glob("nii/*.nii.gz")
    if len(niis) > 0:
        for f in niis:
            os.remove(f)
    
    niiCmd = 'dcm2nii -a y -f y -d n -e n -i n -p n -r Y -o "nii" %s' % (file)
    print niiCmd
    call(shlex.split(niiCmd))

def goProc():
    global  dirsNotFound, options, args
    
    rootdir = os.getcwd()
    for basedir in args:
        os.chdir(rootdir)
        if not os.path.isdir(basedir):
            # not a valid dir, skip
            dirsNotFound.append(basedir)
            continue
    
        os.chdir(basedir)
        search = options.search        
        dirs = glob(search)
        print dirs
        
        absbase = os.getcwd()        
    
        for dti in dirs:
            os.chdir(absbase)
            if not os.path.isdir(dti+"/dicom"):
                dicom2NrrdCmd = 'eddycor.py -s "%s" .' % (search)
                print dicom2NrrdCmd
                call(shlex.split(dicom2NrrdCmd))
            
            os.chdir(dti)
            print os.getcwd()
             
            if os.path.isdir("dicom"):
                file = glob('dicom/*.dcm')[0]
                
                if not os.path.isdir("nii"):
                    os.mkdir("nii")
                    dcm2nii(file)
    
                elif not len(glob("nii/*_FA.nii.gz")) > 0:
                    # Convert dicoms to nii.gz
                    dcm2nii(file)
    
    
                os.chdir("nii")
    
                niiFile = glob("*.nii.gz")[0]
                print niiFile
    
                eddycorGlob = glob('*eddycor.nii.gz*')
                print eddycorGlob
                data = os.path.isfile('data.nii.gz')
                print 'has data.nii.gz=',
                print data
                
                stemname = niiFile.split('_')[0]
                
                if len( eddycorGlob ) == 0 and not data:                    
                    eddyfile = stemname + '_eddycor.nii.gz'
                    print eddyfile
        
                    eddyCmd = 'eddy_correct %s %s 0' % (niiFile, eddyfile)
                    print eddyCmd
    
                    if not os.path.isfile(eddyfile):
                        # fsl eddy current correction            
                        call(shlex.split(eddyCmd))
                else:
                    if data:
                        eddyfile = 'data.nii.gz'
                    else:
                        eddyfile = eddycorGlob[0]
    
                
                betCmd = 'bet %s bet_brain -R -n -m -f %s' % (eddyfile, options.betfrac) 
                print betCmd
                if not os.path.isfile('bet_brain'):
                    call(shlex.split(betCmd))
    
                if ( os.path.isfile('bvecs')):
                    bvecs = 'bvecs'
                else:
                    bvecs = glob("*.bvec")[0]
                
                if ( os.path.isfile('bvals')):
                    bvals = 'bvals'
                else:
                    bvals = glob("*.bval")[0]
                    
                dtifitCmd = 'dtifit --data=%s --out=%s --mask=bet_brain_mask --bvecs=%s --bvals=%s' % (eddyfile, stemname, bvecs, bvals)
                print dtifitCmd
                if len(glob("*_FA.nii.gz")) == 0:
                    call(shlex.split(dtifitCmd))
    
    if len(dirsNotFound) > 0:
        print "These dirs where not found: "
        for i in dirsNotFound:
            print i
    
if __name__ == '__main__':
    parser = OptionParser(usage="Usage: %prog [options] <subject_dir>")
    parser.add_option("-s", "--search", dest="search", default='*DTI*', help="DTI dir name to search for. i.e *DTI*")
    parser.add_option("-f", "--betfrac", dest="betfrac", default='0.2', help='BET command fraction, default = 0.2')
    #parser.add_option("-d", "--dti_dir", dest="dir", help="Only process this directory, if set will ignore -s options and any arg supplied")
    #parser.add_option("-n", "--name", dest="name", help="Base subject name for beautifying output")

    (options, args) = parser.parse_args()

    if len(args) < 1:
        parser.print_help()
        sys.exit(2)
    else:
        goProc()