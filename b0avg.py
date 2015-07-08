#!/usr/bin/python
from glob import glob
from optparse import OptionParser
import os
import sys
import numpy
from pynrrd import NrrdReader

def getOrderStr(ax, num):
    a = numpy.zeros(4, dtype=numpy.int)
    a[ax] = num

    return ' '.join(str(i) for i in a)

class B0avg:
   
    def __init__(self, options, args):
        self.options = options
        self.args = args


    def run(self):
        
        ifile = self.options.input
        ofile = self.options.output
        
        reader = NrrdReader()
        iparams, bindata =  reader.load(ifile)
	#iparams = iparams._data
        
        b0n = iparams['b0num']
        print "%d b0 to be averaged" % b0n
        b0n -= 1

        difcropstr = getOrderStr(options.aorder, b0n)
        orderstr = getOrderStr(options.aorder, b0n)

        print '###########',orderstr

        if options.is_average:
            cmd = "unu crop -i %s -min %s -max M M M M -o tmp.nhdr; " % ( ifile, difcropstr)
            cmd += "unu crop -i %s -min 0 0 0 0 -max %d M M M | unu project -a %s -m mean | unu splice -i grad.nhdr -s - -a 0 -p 0 -o %s; rm tmp.*" % (ifile, b0n, options.aorder, ofile)        
        else:
            cmd = "unu crop -i %s -min %s -max M M M M -o %s " % ( ifile, orderstr, ofile)

        print cmd        
        os.system(cmd)
        
        
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
        for n,i in enumerate(iparams[NrrdReader.grdkey]):
            if count > 0 and n <= b0n:
                continue

            oline =  '%s_%04d:=' % (NrrdReader.grdkey,count)
            for j in i:
                oline += '%1.6f ' % j
            content.append(oline+'\n')
            count+=1
            
            ofileout = open(ofile, 'w')
            for l in content:
                if options.verbose:
                    print l
                ofileout.write(l)
            ofileout.close()
              


if __name__ == '__main__':
    parser = OptionParser(usage="Usage: %prog [options] <subject_dir>")
    parser.add_option("-i", "--input", dest="input", help="input .nhdr file to be averaged")
    parser.add_option("-o", "--output", dest="output", default="b0averaged.nhdr", help="output file name")
    parser.add_option("-a", "--array_order", dest="aorder", type="int", default="0", help="Index position of gradient array in the MR matrix, default is 0 for (1,0,0,0)")
    parser.add_option("-g", "--is_average", dest="is_average", action='store_true', default=False, help="Average the b0s rather than discarding all but the last one")    
    parser.add_option("-v", "--verbose", dest="verbose", action='store_true', default=False, help="print out all debug messages")    

    (options, args) = parser.parse_args()

    if len(args) != 1 and not options.input:
        parser.print_help()
        sys.exit(2)
    else:
        prog = B0avg(options, args)
        prog.run()
