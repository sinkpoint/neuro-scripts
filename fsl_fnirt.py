#!/usr/bin/python
import os, sys
from glob import glob
from optparse import OptionParser

    
class Fnirt:
    def __init__(self, options, args):
        self.options = options
        self.args = args
        self.subjName = ''
        self.subjDir = ''
        
    def go(self):
        if self.options.name:
                self.subjName = self.options.name

        if not self.options.dir:
            if not self.options.search:                
                files = args
            else:
                search = self.options.search
                files = glob(search)
            for file in files:
                self.action(file)
        else:
            self.action(os.listdir(self.options.dir))

    def action(self, filename):
        print filename
        
        if not self.subjName:
            self.subjName = os.path.basename(os.getcwd())

        basename = filename.split('_')[0]

        betfile = basename+"_bet"
        affMat = basename+"_affine.mat"
        flirtfile = basename+"_flirt"
        coeffile = basename+"_fnirt_coef"
        jacfile = basename+"_jac"
        fnirtfile = basename+"_fnirt"
        
        # align FSPGR to MNI reference
        betcmd = "bet "+filename+" "+betfile+" -f 0.35"
        flirtcmd = "flirt -ref /usr/local/fsl/data/standard/MNI152_T1_2mm_brain -in "+betfile+" -omat "+affMat+" -dof 12 -cost corratio -out "+flirtfile
        fnirtcmd = "fnirt --in="+filename+" --aff="+affMat+" --config=T1_2_MNI152_2mm.cnf --cout="+coeffile+" --iout="+fnirtfile+" --jout="+jacfile+" --jacrange=0.1,10"
        
        # linear register FRFSE T2 to FSPGR
        t2flirtcmd = "flirt -ref "+basename+"_FSPGR -in "+basename+"_FRFSE_0 -omat "+basename+"_frfse_2_fspgr.mat -dof 12 -cost corratio -out "+basename+"_frfse_2_fspgr"
        # apply linear regiser transform to ROI volume
        roiflirtcmd = "flirt -in "+basename+"_roi -ref "+basename+"_FSPGR -out "+basename+"_roi_flirt -interp nearestneighbour -applyxfm -init "+basename+"_frfse_2_fspgr.mat"
        # apply warp transform to linearly registered ROI
        roiwarpcmd = "applywarp -i "+basename+"_roi_flirt -r /usr/local/fsl/data/standard/MNI152_t1_2mm --interp=nn -o "+basename+"_roi_fnirt -w "+basename+"_fnirt_coef.nii.gz"       
        # binarize the interpolated roi volume
        #roibincmd = "fslmaths "+basename+"_roi_fnirt -bin "+basename+"_roi_fnirt"
        
        invwarpcmd = "invwarp --warp="+basename+"_fnirt_coef --ref="+basename+"_roi_flirt --out="+basename+"_fnirt_inv_coef"
        applyinvwarpcmd = "applywarp -i agg_map -r "+basename+"_roi_flirt --interp=nn -o "+basename+"_roi_agg -w "+basename+"_fnirt_inv_coef"
        
        #print betcmd
        #os.system(betcmd)
        #print flirtcmd
        #os.system(flirtcmd)
        #print fnirtcmd
        #os.system(fnirtcmd)
        
        #print t2flirtcmd
        #os.system(t2flirtcmd)
        
        print roiflirtcmd
        os.system(roiflirtcmd)
        
        print roiwarpcmd
        os.system(roiwarpcmd)
        
        print invwarpcmd
        os.system(invwarpcmd)
        print applyinvwarpcmd
        os.system(applyinvwarpcmd)


if __name__ == '__main__':
    parser = OptionParser(usage="Usage: %prog [options] files")
    parser.add_option("-s", "--search", dest="search", help="DTI dir name to search for. i.e *DTI*")
    parser.add_option("-d", "--dir", dest="dir", help="Only process this directory, if set will ignore -s options and any arg supplied")
    parser.add_option("-n", "--name", dest="name", help="Base subject name for beautifying output")

    (options, args) = parser.parse_args()

    if len(args) < 1 and not options.dir and not options.search:
        parser.print_help()
        sys.exit(2)
    else:
        prog = Fnirt(options, args)
        prog.go()

