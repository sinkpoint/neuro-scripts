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
		
	def goCor(self):
		if options.name:
				self.subjName = self.options.name

		if not options.dir:
			self.subjDir = args[0]
			if not self.subjName:
				self.subjName = self.subjDir

			search = self.options.search
			os.chdir(self.subjDir)
			dirs = glob(search)
			print dirs
			for dti in dirs:
				self.doConv(dti)
		else:
			self.doConv(self.options.dir)

	def doConv(self, dir):
		if not self.subjName:
			self.subjName = os.path.basename(os.getcwd())

		os.chdir(dir)
		print os.getcwd()

		dtiname = self.subjName + dir
		dtiname = dtiname.replace('/', '')

		if not os.path.isdir("dicom"):
			print 'make dicom and nrrd dirs'
			os.mkdir("dicom")
			os.mkdir("nrrd")
			os.system("mv *.dcm dicom")

		outputfile = dtiname + ".nhdr"
		print outputfile

		dcm2nrrd = os.getenv('SLICER_HOME') + "/lib/Slicer3/Plugins/DicomToNrrdConverter"
		cmd = dcm2nrrd + " --inputDicomDirectory dicom --outputDirectory nrrd --outputVolume " + outputfile
		print cmd
		os.system(cmd)



if __name__ == '__main__':
	parser = OptionParser(usage="Usage: %prog [options] <subject_dir>")
	parser.add_option("-s", "--search", dest="search", default='*DTI*', help="DTI dir name to search for. i.e *DTI*")
	parser.add_option("-d", "--dir", dest="dir", help="Only process this directory, if set will ignore -s options and any arg supplied")
	parser.add_option("-n", "--name", dest="name", help="Base subject name for beautifying output")

	(options, args) = parser.parse_args()

	if len(args) != 1 and not options.dir:
		parser.print_help()
		sys.exit(2)
	else:
		prog = Eddycor(options, args)
		prog.goCor()

