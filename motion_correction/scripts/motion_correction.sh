#!/bin/bash -l 
# Script to perform general inter-slice motion correction
# Written: David Rotenberg
# Date 29 July 2013

args="$@"
scan=$1

echo "Motion Correction Start"
echo "Correcting Scan: $scan"

# Split the volume into components
fslsplit $scan

# Loop and bet all with f=0.1
for vol in vol*nii*;
do
gunzip $vol
volume=$(basename $vol .nii.gz)
volname=$( basename $volume .nii);
echo "Betting: $volume"
bet "$vol" "$volname"_bet -R -f 0.1
gunzip "$volname"_bet.nii.gz

echo "Registering: $volname"
# Generate linear transform from B-ZERO to T2
flirt -interp sinc -sincwidth 7 -noresample -noresampblur -sincwindow blackman -in ""$volname"_bet.nii" -ref vol0000_bet.nii.gz -nosearch -out "$volname"_reg.nii.gz -omat "$volname"_trans.xfm -paddingsize 1
done

bash ./transpose.sh dwi.bvec > dirs_62.dat
cat *_trans.xfm > Transforms.txt
matlab -nojvm < finitestrain.m
perl dattonrrd.pl newdirs.dat newdirs.nhdr

fslmerge -t Motion_Corrected_DWI.nii.gz *reg.nii.gz

# Conversion to NRRD
# Require DWI.bval and DWI.bvec filenames
cp dwi.bval DWI.bval
cp dwi.bvec DWI.bvec
gunzip Motion_Corrected_DWI.nii.gz
python nifti2nrrd -i Motion_Corrected_DWI.nii
cat DWI.nhdr | head -18 > DWI_BASE.nhdr
cat newdirs.nhdr >> DWI_BASE.nhdr
