#!/usr/bin/python
import os, sys
from glob import glob
from optparse import OptionParser

	
class Eddycor:
	def __init__(self, options, args):
		self.options = options
		self.args = args
		self.subjName = ''
		self.subjDir = ''
		self.eddycorFileName =''
		self.force = False
		
	def goCor(self):
		os.chdir(args[0])
		self.subjDir = os.getcwd()
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
		
		if os.path.isfile(IS_PROCESSING_FILE):
			print dir + ' is already being processed, skipping'
			return
		elif os.path.isfile(DONE_PROCESSING_FILE) and not self.force: 
			print dir + ' is already processed, skipping'	
			return
		else:
			os.system("touch "+IS_PROCESSING_FILE)
			
			
		self.doPreprocess(dir)
		
		if (options.motion):
			self.doFSLCorrection(dir)
		elif (options.nrrd):
			self.doNrrdEddyCor(dir)
		elif (options.all):
			self.doNrrdEddyCor(dir)	
			self.doFSLCorrection(dir)
		else:
			self.doNrrdEddyCor(dir)
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

		
	def doFSLCorrection(self, dir, veconly=False):
		
		#dcm2nii = "dcm2nii -d N -e N -f Y -i N -o . ../dicom/*_0.dcm"
		nrrdname = self.subjName
		
		if not os.path.isdir("nifti"):
			print 'make nifti folder'
			os.mkdir('nifti')
		os.chdir("nifti")		
		
		nrrdname = self.subjName
			
		if not os.path.isfile(nrrdname+'.nii.gz'):
			print 'convert dicom to nifti'			
			cmd = "dcm2nii -d N -e N -f Y -i N -p N -o . ../dicom/%s" % (self.options.dicom_filter)
			os.system(cmd)	
			
					
			nii_file = glob("*.nii.gz")[0]
			base = os.path.splitext(os.path.splitext(nii_file)[0])[0]
			
			os.rename(base+".nii.gz", nrrdname+".nii.gz")
			os.rename(base+".bvec", nrrdname+".bvec")
			os.rename(base+".bval", nrrdname+".bval")
			
			#cmd = "DWIConvert --inputDicomDirectory ../dicom --outputVolume %s.nii.gz --conversionMode DicomToFSL" % (nrrdname)
		
		
#		else:
#			cmd = "DWIConvert --inputVolume ../nrrd/%s.nhdr --outputVolume %s.nii.gz --conversionMode NrrdToFSL --outputBVectors %s.bvec --outputBValues %s.bval" % (nrrdname, nrrdname, nrrdname, nrrdname)	
#			print 'convert nrrd to nifti'
			
		
		motioncorCmd = "motion_correction.sh "
		if self.options.veconly:
			motioncorCmd += "-v "
		motioncorCmd += nrrdname
		
		os.system(motioncorCmd)
		
		os.chdir('..')



if __name__ == '__main__':
	parser = OptionParser(usage="Usage: %prog [options] <subject_dir>")
	parser.add_option("-s", "--search", dest="search", default='*DTI*', help="DTI dir name to search for. i.e *DTI*")
	parser.add_option("-d", "--dti_dir", dest="dir", help="Only process this directory, if set will ignore -s options and any arg supplied")
	parser.add_option("-n", "--name", dest="name", help="Base subject name for beautifying output")
	parser.add_option("-m", "--motion", action="store_true", dest="motion", help="Perform motion correction involving only FSL")
	parser.add_option("-v", "--veconly", action="store_true", dest="veconly", help="Assumes FLIRT has already been done. Perform vector calculation only")
	parser.add_option("-r", "--nrrd", action="store_true", dest="nrrd", help="Perform tend eddy current only")
	
	parser.add_option("-a", "--all", action="store_true", dest="all", help="Perform all correction steps")	
	parser.add_option("-p", "--skip", action="store_true", dest="skip", help="Skip folders that contain processed files")	
	parser.add_option("-f", "--force", action="store_true", dest="force", help="Force run even if already done running on this subject")	
	parser.add_option("-z", "--dicom_filter", dest="dicom_filter", default='*.dcm', help="String used to search for dicoms to convert, default=*.dcm") 
	(options, args) = parser.parse_args()

	if len(args) != 1 and not options.dir:
		parser.print_help()
		sys.exit(2)
	else:
		prog = Eddycor(options, args)
		prog.goCor()

