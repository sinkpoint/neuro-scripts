#!/usr/bin/python
from glob import glob
from optparse import OptionParser
import os
import sys
import numpy
from nrrd import NrrdReader

class B0avg:
   
    def __init__(self, options, args):
        self.options = options
        self.args = args
    def run(self):
        
        ifile = self.options.input
        ofile = self.options.output
        
        reader = NrrdReader()
        iparams =  reader.getFileContent(ifile)
        
        b0n = iparams['b0num']
        print "%d b0 to be averaged" % b0n
        b0n -= 1
        aorder = numpy.zeros(4)
        aidx = options.aorder
        aorder[aidx] = b0n
        orderstr = ""
        for i in aorder:
            orderstr += '%d ' %(i)
        cmd = "unu crop -i %s -min %s -max M M M M -o %s" % ( ifile, orderstr, ofile)        
        print cmd
        
        os.system(cmd)
        #cmd = "unu crop -i %s -min 0 0 0 0 -max %d M M M | unu project -a 0 -m mean | unu splice -i grad.nhdr -s - -a 0 -p 0 -o %s" % (ifile, b0n, ofile)        
        #print cmd
        #os.system(cmd)
        
        ofilein = open(ofile,'r')
        content = []
        while ofilein:
            line = ofilein.readline()            
            if len(line) == 0:
                break;
            if line.startswith(NrrdReader.grdkey):
                continue
            content.append(line)
        ofilein.close()
        
        
        count = 0
        for i in iparams[NrrdReader.grdkey]:
            oline =  '%s_%04d:=' % (NrrdReader.grdkey,count)
            for j in i:
                oline += '%1.6f ' % j
            content.append(oline+'\n')
            count+=1
            
            ofileout = open(ofile, 'w')
            for l in content:
                print l
                ofileout.write(l)
            ofileout.close()
              


if __name__ == '__main__':
    parser = OptionParser(usage="Usage: %prog [options] <subject_dir>")
    parser.add_option("-i", "--input", dest="input", help="input .nhdr file to be averaged")
    parser.add_option("-o", "--output", dest="output", default="b0averaged.nhdr", help="output file name")
    parser.add_option("-a", "--array_order", dest="aorder", type="int", default="0", help="Index position of gradient array in the MR matrix, default is 0 for (1,0,0,0)")    

    (options, args) = parser.parse_args()

    if len(args) != 1 and not options.input:
        parser.print_help()
        sys.exit(2)
    else:
        prog = B0avg(options, args)
        prog.run()
