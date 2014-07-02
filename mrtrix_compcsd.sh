#!/bin/bash -l 
# Script to perform all steps to get CSD estimate with mrtrix
# Written: David Qixiang Chen

usage()
{
	cat<<EOF
	usage: $0 options arg
	
	OPTIONS:
		-g  Gradient file 

	ARG
		DWI image file
EOF
}

args=("$@")

GRAD=""
DWI=""

OPTIND=0

while getopts "g:" OPTION
do
	echo "opt $OPTION arg $OPTARG ind $OPTIND"
	case $OPTION in
		g)
			GRAD=$OPTARG
			;;
		?)
			usage
			exit
			;;
	esac
done
	echo $OPTION $OPTARG $OPTIND

if [ -n "${!OPTIND}" ]
	then DWI="${!OPTIND}"
else 
	usage
	exit
fi

rm mask.mif
#average $DWI -axis 3 - | threshold -percent 5 - - | median3D - - | median3D - mask.mif
bet2 Motion_Corrected_DWI_nobet.nii.gz dwibet -m -n -f 0.1
mrconvert dwibet_mask.nii.gz mask.mif -datatype Bit

# rm dt.mif
# dwi2tensor $DWI dt.mif -grad $GRAD
# rm fa.mif
# tensor2FA dt.mif - | mrmult - mask.mif fa.mif
# rm ev.mif
# tensor2vector dt.mif - | mrmult - fa.mif ev.mif
# rm sf.mif
# erode mask.mif -npass 3 - | mrmult fa.mif - - | threshold - -abs 0.7 sf.mif
# rm response.txt
dwi2response -nthreads 8 -mask mask.mif -grad $GRAD $DWI response.txt 
#disp_profile -response response.txt &

#while true; do
#read -p "Response profile satisfactory? Continue with CSD estimate?" yn
#	case $yn in
#		[Yy]* ) break;;
#		[Nn]* ) exit;;
#		* ) echo "Please answer yes or no.";; 
#	esac
#done

rm CSD8.mif
#csdeconv $DWI response.txt -lmax 8 -mask mask.mif CSD8.mif -grad $GRAD
dwi2fod -nthreads 8 -mask mask.mif -grad $GRAD $DWI response.txt CSD8.mif 
