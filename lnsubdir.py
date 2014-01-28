#!/usr/bin/python

import os,sys,glob

fromdir = sys.argv[1]
foldername = sys.argv[2]

localdir = os.getcwd()

os.chdir(fromdir)
fromdir = os.getcwd()
dirs = os.listdir(".")

for dir in dirs:
    path = fromdir+'/'+dir+'/'
    os.chdir(path)
    sub = glob.glob('*'+foldername+'*')
    path += sub[0]
    os.chdir(localdir)
    print path
    os.symlink(path, dir)
    
    




