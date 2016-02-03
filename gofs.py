#!/usr/bin/env python

# Author: David Qixiang Chen
# email: qixiang.chen@gmail.com
# 
# Automates multiple instances of freesurfer recon-all executions. 

import sys, os, re, subprocess, time, shlex
from optparse import OptionParser
from os import path

options = []
args = []

def init():
    global options, args
    subjdir = args[0]
    env_subj = os.getenv('SUBJECTS_DIR')
    subjdir = env_subj + '/' + subjdir

    origdir = subjdir + '/' + options.orig

    if not os.path.exists(subjdir):
        print "Subjectdir at" + subjdir + " not found."
        sys.exit(2)
    if not os.path.exists(origdir):
        print "Original scans at " + origdir + " not found."
        origdir = False

    # passed dir checks             
    os.putenv('SUBJECTS_DIR', subjdir)
    return (subjdir, origdir)

def gofs():
    global options, args
    targetmap = {}
    print args
    
    if options.subj:
        subjs = options.subj.split(" ")
        print subjs
        for s in subjs:
            targetmap[s] = s
    
    else:
        (subjdir, origdir) = init()
       
        procs = listFolders(subjdir)
        procs.sort();
        
        if ( "fsaverage" in procs ):
            procs.remove("fsaverage")
            
        if ( "qdec" in procs ):
            procs.remove("qdec")    
            
        print "=========================== GO FS =================================\n"
        
        print "Subjects in subjdir:"
        printNames(procs)
        origs_map = {}

        if ( origdir ):
            from glob import glob
            orig_files = glob(origdir+'/*.nii*')
            for i in orig_files:
                origs_map[path.basename(i)] = 'nii'

            origs = listFolders(origdir)
            for i in origs:
                origs_map[i] = 'dir'

            orig_keys = origs_map.keys()
            dones = list(set(orig_keys).intersection(set(procs)))
            fresh = list(set(orig_keys).difference(set(procs)))
            
            print "= All available scans with originals found:"
            print '-- Possible input files: '
            for i in orig_files:
                print path.basename(i)
            print '-- Folders '
            printNames(origs)
            print ""

            print "= Processed scans found:"
            printNames(dones)  

            print '= Unprocessed:'     
            printNames(fresh)
        
        
            print "\nWhich group do you want to process? (a)ll/(p)rocessed/(u)nprocessed) >",
            ans = getAns(('a', 'p', 'u'))
        
            subjs = {
                'a': origs_map.keys(),
                'p': dones,
                'u': fresh,
            }.get(ans)
        else:
            subjs = procs
    
        print "We are gonna process these subjects:"
        print subjs
    
        
        # has_dicom = False
        # for i in subjs:
        #     print i, origs_map[i]
        #     if origs_map[i] == 'dir':
        #         has_dicom = True
        #         targetmap[i] = ''
        #     else:
        #         targetmap[i] = '..'
        
        for i in subjs:
            targetmap[i] = {'name':i,'type':origs_map[i]}
                

        if len(origs) > 0 and (options.stage == 'a' or options.stage == '1'): 
            print "\nThe filename of the first file in each DICOM series is needed for processing."
            print "You want to enter the filenames manually? (y/n) >",
            ans = getAns()
            if ans == 'y':
                print "\nAre series named identically? >",
                ans = getAns()
                if ans == 'y':
                    print "\nPlease enter the first filename (i.e. scan0.dcm ) for all anat series"
                    print "> ",
                    sname = raw_input()
                    for i in subjs:
                        if origs_map[i] == 'dir':
                            targetmap[i]['name'] = sname
                else:
                    for i in subjs:
                        if origs_map[i] == 'dir':
                            print "\nfilename for " + i + " (i.e. scan_01.dcm: >",
                            targetmap[i]['name'] = raw_input()
            else :
                for i in subjs:
                    if origs_map[i] == 'dir':
                        targetmap[i]['name'] = "*"+options.extpad

        for k,v in targetmap.iteritems():
            print k,v

    if not options.test:
        reconall(targetmap)


def reconall(targetmap, maxinst=8):
    global options, args


    stagemap = {
        'a':'-all',
        '1':'-autorecon1',
        '2':'-autorecon2',
        '3':'-autorecon3',
        '4':'-qcache',
    }

    if (options.mstage):
        stages = options.mstage
    else:
        stages = ''
        st = ['1', '2', '3', '4']
        for i in st:
            if i in options.stage:
                stages += stagemap.get(i) + ' '
        if stages == '':
            stages = '-all -qcache'




    subjnum = len(targetmap)
    keys = targetmap.keys()
    instnum = 0
    i = 0
    sleeptime = 2
    jobnum = 0
    print "==================<| START FS PROCESSING > |>===================="
    while instnum < subjnum:
        print 'Elapsed %d seconds' % (i*sleeptime)
        print 'Instance Num %d/%d' % (instnum, subjnum)
        print "==== Current jobs ===="
        subprocess.Popen("ps auwx | awk '{print $1,$13, $14, $15}' | grep /bin/recon-all | sort | uniq", shell=True)
        jobcom = subprocess.Popen("ps auwx | awk '{print $1,$13, $14, $15, $16}' | grep /bin/recon-all | sort | uniq | wc -l", shell=True, stdout=subprocess.PIPE)
        [jobnum, errstd] = jobcom.communicate()
        jobnum = int(jobnum)
        print 'number of jobs: %d' % jobnum

        key_label = keys[instnum]
        name = path.basename(key_label)

        if jobnum < options.max:
            print "====================| NOW PROCESSING <" + name + " (%d/%d) > |>=====================" % (instnum + 1, subjnum)

            if (options.stage == 'a' or options.stage == '1') and options.mstage == None:
                input_path = '$SUBJECTS_DIR/' + options.orig
                tval = targetmap[key_label]
                if tval['type']=='dir':
                    input_path += '/' + name

                input_path += '/' + targetmap[key_label]['name']
                racmd = 'recon-all -use-gpu -i '+ input_path + ' ' + stages + ' ' + ' -s ' + name + ' ' + options.cmd
            else:
                racmd = 'recon-all -use-gpu ' + stages + ' ' + ' -s ' + name + ' ' + options.cmd

            cmd = 'screen -dmLS '+name+' bash -i -c "' + racmd + '"'
            print cmd
            subprocess.Popen(shlex.split(cmd))
            #os.system(cmd)
            instnum = instnum + 1
        time.sleep(sleeptime)
        i = i + 1







def printNames(inp):
    for i in inp:
        print path.basename(i),
    print ""

def getAns(rep=['y', 'n']):
    ans = ''
    while (ans not in rep):
        ans = raw_input()
    return ans

def listFolders(dir):
    dr = os.listdir(dir)
    return [name for name in os.listdir(dir)
        if os.path.isdir(os.path.join(dir, name))]


if __name__ == '__main__':
    parser = OptionParser(usage="Usage: %prog [options] fsSubjectsDir")
    parser.add_option("-s", "--stage", dest="stage", default='a', help="Stage of recon-all to run. \nOptions: 'a' '1' '2' '3' '4'. default is 'a'. \nAny mixture of 1234 will start these steps in combination.")
    parser.add_option("-j", "--subjects", dest="subj", help="Manually define a list of subjects to run")
    #parser.add_option("-z", "--mgz", dest="is_mgz", action='store_true', default=False, help="Files in the _orig_ folder are in mgz format")
    parser.add_option("-m", "--manualStage", dest="mstage", help="Manually define the recon stages as recon-all parameters")
    parser.add_option("-o", "--orig", dest="orig", default='_orig_', help="folder name of original scans, default is '_orig_'")
    parser.add_option("-c", "--cmd", dest="cmd", default='', help="Additional options to add to recon-all manually")
    parser.add_option("-x", "--max", dest="max", type='int', default=7, help="Maximum number of concurrent fs processes, default is 7")
    parser.add_option("-p", "--extpad", dest="extpad", default='_0.dcm', help="The string to pad onto auto-detected subject names, i.e C01-> C01_0.dcm; '_0.dcm' is the default padding string.")
    parser.add_option("-t", "--test", action='store_true', dest="test", default=False, help="Test mode. Don't actually run freesurfer.")
    (options, args) = parser.parse_args()

    if len(args) != 1:
        parser.print_help()
        sys.exit(2)
    else:
        gofs()






