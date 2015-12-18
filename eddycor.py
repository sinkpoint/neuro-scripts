#!/usr/bin/env python
import os, sys
from glob import glob
from optparse import OptionParser


class Eddycor:
    def __init__(self, options, args):
        self.options = options
        self.args = args
        self.subjName = options.name
        self.subjDir = ''
        self.eddycorFileName =''
        self.force = False

    def goCor(self):
        if len(args) > 0:
            os.chdir(args[0])
        self.subjDir = os.getcwd()
        if not self.subjName:
            self.subjName = os.path.basename(os.getcwd())
        self.force = self.options.force

        if not options.dir:
            search = self.options.search
            dirs = glob(search)
            print dirs
            for dti in dirs:
                self.doCor(dti)
        else:
            self.doCor(self.options.dir)


    def doCor(self, dir):

        os.chdir(dir)
        print os.getcwd()

        PROCESSED_FILE = 'DWI_CORRECTED.nhdr'

        if self.options.skip:
            if os.path.isfile(PROCESSED_FILE):
                print dir + " already processed"
                return

        IS_PROCESSING_FILE = "isProcessing.tmp"
        DONE_PROCESSING_FILE = "doneProcessing.tmp"

        if os.path.isfile(IS_PROCESSING_FILE) and not self.force:
            print dir + ' is being processed, skipping'
            return
        elif os.path.isfile(DONE_PROCESSING_FILE) and not self.force:
            print dir + ' is already processed, skipping'
            return
        else:
            os.system("touch "+IS_PROCESSING_FILE)


        self.doPreprocess(dir)

        if (options.is_fsl):
            self.doFSLCorrection(dir)
        elif (options.is_ants):
            self.doAntsCorrection(dir)
        elif (options.is_nrrd):
            self.doNrrdEddyCor(dir)
        elif (options.is_all):
            self.doNrrdEddyCor(dir)
            self.doFSLCorrection(dir)
            self.doAntsCorrection(dir)            
        else:
            self.doFSLCorrection(dir)

        os.remove(IS_PROCESSING_FILE)
        os.system('touch '+DONE_PROCESSING_FILE)


    def doPreprocess(self, dir):
        #self.subjName = os.path.basename(os.getcwd())
        EDDY_AFFIX = "_eddycor"
        self.eddycorFileName = self.subjName+EDDY_AFFIX

        if not os.path.isdir("dicom"):
            print 'make dicom dirs'
            os.mkdir("dicom")
            os.system("mv %s dicom" % (self.options.dicom_filter))

    def doNrrdEddyCor(self, dir):
        if not os.path.isdir("nrrd"):
            os.mkdir("nrrd")

        rawNrrdFile = self.subjName + ".nhdr"
        eddyCorFile = self.eddycorFileName + ".nhdr"

        if not os.path.isfile('nrrd/'+rawNrrdFile):
            #dcm2nrrd = "${SLICER3_HOME}/lib/Slicer3/Plugins/DicomToNrrdConverter"
            slicer4 = os.getenv('SLICER4_HOME')
            cli_path = glob(slicer4+'/lib/Slicer*')
            if len(cli_path) == 0:
                print 'enviornment variable $SLICER4_HOME is not defined'
                return
            ldpath=cli_path[0]
            expath=cli_path[0] + '/cli-modules'
            dcm2nrrd = "LD_LIBRARY_PATH=%s:%s %s/DicomToNrrdConverter" % (ldpath, expath, expath)
            cmd = dcm2nrrd + " --inputDicomDirectory dicom --outputDirectory nrrd --outputVolume " + rawNrrdFile
            print cmd
            os.system(cmd)

        tendcmd = "tend epireg -i nrrd/" + rawNrrdFile + " -o nrrd/" + eddyCorFile + " -f 0.65 -g kvp"
        print tendcmd
        os.system(tendcmd)

    def doNiftiPrepare(self, dir):
        #dcm2nii = "dcm2nii -d N -e N -f Y -i N -o . ../dicom/*_0.dcm"
        subjname = self.subjName
        if not os.path.isdir("nifti"):
            print 'make nifti folder'
            os.mkdir('nifti')
        os.chdir("nifti")


        if not os.path.isfile(subjname+'.nii.gz'):
            print 'convert dicom to nifti'
            cmd = "dcm2nii -d N -e N -f Y -i N -p N -o . ../dicom/%s" % (self.options.dicom_filter)
            os.system(cmd)


            nii_file = glob("*.nii.gz")[0]
            base = os.path.splitext(os.path.splitext(nii_file)[0])[0]

            os.rename(base+".nii.gz", subjname+".nii.gz")
            os.rename(base+".bvec", subjname+".bvec")
            os.rename(base+".bval", subjname+".bval")
        os.chdir('..')

    def doFSLCorrection(self, dir, veconly=False):
        self.doNiftiPrepare(dir)
        os.chdir("nifti")
        subjname = self.subjName


            #cmd = "DWIConvert --inputDicomDirectory ../dicom --outputVolume %s.nii.gz --conversionMode DicomToFSL" % (subjname)


#        else:
#            cmd = "DWIConvert --inputVolume ../nrrd/%s.nhdr --outputVolume %s.nii.gz --conversionMode NrrdToFSL --outputBVectors %s.bvec --outputBValues %s.bval" % (subjname, subjname, subjname, subjname)
#            print 'convert nrrd to nifti'


        motioncorCmd = "motion_correction.sh "
        if self.options.is_veconly:
            motioncorCmd += "-v "
        motioncorCmd += subjname

        os.system(motioncorCmd)

        #flip vectors
        import flipGradVectors as fgv        
        ax = options.invert_vecs
        if not ax=='none':
            fgv.flip_file('DWI_CORRECTED.nhdr','DWI_CORRECTED.nhdr', axis=ax)
            fgv.flip_file('newdirs.dat','newdirs.dat', axis=ax)

        os.chdir('..')

    def doAntsCorrection(self, dir, veconly=False):
        self.doNiftiPrepare(dir)
        os.chdir('nifti')
        #split scans

        cmd='fslsplit %s.nii.gz' % (self.subjName)
        os.system(cmd)

        print '# Register to baseline with ANTs'

        vols = glob('vol*nii.gz')
        baseline='vol0000.nii.gz'
        for v in vols:
            base=v.split('.')[0]
            output=base
            #output_trans=output+'0GenericAffine.mat'
            output_trans=output+'Affine.txt'
            output_warped=base+'_ants.nii.gz'
            ref=baseline
            fin=v
            metric='MI[%s,%s,1,32]' % (fin, ref)
            trans='Affine[0.75]'
            conv='[1000x1000x1000,1e-6,5]'
            shrinkf='4x2x1'
            smoothsig='4x2x1'
            #cmd='antsRegistration -d 3 --output '+output+' --metric '+metric+' --transform '+trans+' --convergence '+conv+' --shrink-factors '+shrinkf+' --smoothing-sigmas '+smoothsig+' --use-estimate-learning-rate-once'
            cmd='antsaffine.sh 3 '+baseline+' '+v
            os.system(cmd)
            cmd='antsApplyTransforms -d 3 -r '+ref+' -i '+fin+' -t '+output_trans+' -o '+output_warped
            os.system(cmd)
            cmd='ConvertTransformFile 3 '+output_trans+' '+base+'_trans.xfm --hm --ras'
            os.system(cmd)

        mergefile='Motion_Corrected_DWI_nobet.nii.gz'
        cmd='fslmerge -t '+mergefile+' vol*_ants.nii.gz'
        os.system(cmd)

        cmd = "motion_correction.sh -v "
        cmd += self.subjName
        os.system(cmd)

        os.chdir('..')







if __name__ == '__main__':
    parser = OptionParser(usage="Usage: %prog [options] <subject_dir>")
    parser.add_option("-s", "--search", dest="search", default='*DTI*', help="DTI dir name to search for. i.e *DTI*")
    parser.add_option("-d", "--dti_dir", dest="dir", help="Only process this directory, if set will ignore -s options and any arg supplied")
    parser.add_option("-n", "--name", dest="name", help="Base subject name for beautifying output")
    parser.add_option("-m", "--fsl", action="store_true", dest="is_fsl", help="Perform motion correction involving only FSL")
    parser.add_option("-t", "--ants", action="store_true", dest="is_ants", help="Perform motion correction using ANTs")
    parser.add_option("-v", "--veconly", action="store_true", dest="is_veconly", help="Assumes registrations has already been done. Perform vector calculation only")
    parser.add_option("-i", "--invert_vecs", dest="invert_vecs", default='1', help="Invert the final gradient vectors along an axis, comma-separated, i.e 0,1,2 for x,y,z; default is 1 for Y axis. To turn off use 'none'")
    parser.add_option("-r", "--nrrd", action="store_true", dest="is_nrrd", help="Perform tend eddy current only")

    parser.add_option("-a", "--all", action="store_true", dest="is_all", help="Perform all correction steps")
    parser.add_option("-p", "--skip", action="store_true", dest="skip", help="Skip folders that contain processed files")
    parser.add_option("-f", "--force", action="store_true", dest="force", help="Force run even if already done running on this subject")
    parser.add_option("-z", "--dicom_filter", dest="dicom_filter", default='*.dcm', help="String used to search for dicoms to convert, default=*.dcm")
    (options, args) = parser.parse_args()


    prog = Eddycor(options, args)
    prog.goCor()

