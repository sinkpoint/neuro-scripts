#!/bin/bash -l 
# Script to perform general inter-slice motion correction
# Written: David Rotenberg
# Date 29 July 2013

MOTION_HOME="/home/dchen/motion_correction"
args="$@"
scan=$1

echo "Motion Correction Start"
echo "Correcting Scan: $scan"

echo "Calculating transforms"

bash $MOTION_HOME/transpose.sh $scan.bvec > dirs_62.dat
cat *_trans.xfm > Transforms.txt
matlab -nojvm < $MOTION_HOME/finitestrain.m
perl $MOTION_HOME/dattonrrd.pl newdirs.dat newdirs.nhdr


echo "Convert to nrrd"

# Conversion to NRRD
# Require DWI.bval and DWI.bvec filenames
cp $scan.bval DWI.bval
cp $scan.bvec DWI.bvec
gunzip Motion_Corrected_DWI.nii.gz
python $MOTION_HOME/nifti2nrrd -i Motion_Corrected_DWI.nii
cat DWI.nhdr | head -18 | sed -e 's/float32/float/g' > DWI_CORRECTED.nhdr
cat newdirs.nhdr >> DWI_CORRECTED.nhdr


