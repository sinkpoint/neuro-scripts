#!/bin/bash -l 
# Script to perform general inter-slice motion correction
# Written: David Rotenberg
# Modified: David Qixiang Chen

usage()
{
	cat<<EOF
	usage: $0 options arg
	
	OPTIONS:
		-a	Affix to append to images and transforms. Default is "_nobet"
		-v	Vector calculations only. 
		-o	Output file name, without extension. Default is DWI_CORRECTED
	
	ARG
		Name of reference file without extension.
EOF
}

MOTION_HOME=${HLAB_SCRIPT_PATH}/motion_correction

args=("$@")
affix="_nobet"
dwi_out="DWI_CORRECTED.nhdr"
mcored_file="Motion_Corrected_DWI"$affix""

MOTION_COR_ONLY=false

OPTIND=0

while getopts "a:vo:" OPTION
do
#	echo "opt $OPTION arg $OPTARG ind $OPTIND"
	case $OPTION in
		a)
			affix=$OPTARG
			;;
		v)
			echo 'motion_cor only'
			MOTION_COR_ONLY=true
			;;
		o)
			dwi_out=$OPTARG
			;;
		?)
			usage
			exit
			;;
	esac
done
#echo $OPTION $OPTARG $OPTIND

if [ -n "${!OPTIND}" ]
	then scan="${!OPTIND}"
else 
	usage
	exit
fi

echo "Motion Correction Start"
echo "Correcting Scan: $scan"

echo "Split scans"
# Split the volume into components
fslsplit $scan.nii.gz

echo "Register to baseline"
# Loop and bet all with f=0.1
for vol in vol*nii.gz
do
#	gunzip $vol
	volume=$(basename $vol .nii.gz)
	volname=$( basename $volume .nii);
	#echo "Betting: $volume"
	#bet "$vol" "$volname"_bet -R -f 0.1
#	gunzip "$volname"_bet.nii.gz


	echo "Registering: $volname"
	# Generate linear transform from B-ZERO to T2
#		flirt -in ""$volname"_bet.nii.gz" -ref vol0000_bet.nii.gz -nosearch -omat "$volname"_trans.xfm -noresample -noresampblur -interp spline -out "$volname"_reg.nii.gz -paddingsize 1
	if ! $MOTION_COR_ONLY; then
		flirt -in ""$volname".nii.gz" -ref vol0000.nii.gz -nosearch -noresampblur -omat "$volname"_trans"$affix".xfm -interp spline -out "$volname"_reg"$affix".nii.gz -paddingsize 1
	else
		echo "Apply transform: $volname"					
		flirt -interp spline -in "$volname" -ref vol0000.nii.gz -out "$volname"_reg"$affix".nii.gz -applyxfm -init  "$volname"_trans"$affix".xfm -paddingsize 1
	fi
	#echo "Apply transform: $volname"	
	#resample on the original
	#flirt -interp spline -in "$volname" -ref vol0000.nii.gz -out "$volname"_reg.nii.gz -applyxfm -init  "$volname"_trans.xfm -paddingsize 1
done

echo "fslmerge"

fslmerge -t "$mcored_file".nii.gz *reg"$affix".nii.gz

rm vol*nii*	


echo "Calculating transforms"

bash $MOTION_HOME/transpose.sh $scan.bvec > dirs_62.dat
cat *trans*.xfm > Transforms.txt
#matlab -nojvm < $MOTION_HOME/finitestrain.m
finitestrain.py -t Transforms.txt -i dirs_62.dat -o newdirs.dat
perl $MOTION_HOME/dattonrrd.pl newdirs.dat newdirs.nhdr

echo "Convert to nrrd"

# Conversion to NRRD

DWIConvert --inputBVectors $scan.bvec --inputBValues $scan.bval --inputVolume $mcored_file.nii.gz --outputVolume tmp.nrrd --conversionMode FSLToNrrd
unu save -i tmp.nrrd -o $dwi_out -f nrrd
rm tmp.nrrd

cat $dwi_out | head -19  > tmp.nhdr
cat newdirs.nhdr >> tmp.nhdr
mv tmp.nhdr $dwi_out


