#!/bin/bash

usage()
{
	cat<<EOF
	usage: $0 options arg
	
	OPTIONS:
	
	ARG
		Name of reference file without extension.
EOF
}

cli=$SLICER4_HOME/lib/Slicer-4.3/cli-modules
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$SLICER4_HOME/lib/Slicer-4.3:$LD_LIBRARY_PATH:$SLICER4_HOME/lib/Slicer-4.3/cli-modules:$SLICER4_HOME/lib/Teem-1.10.0

args=("$@")

dwi_file=""
tensor_file=""
label_file=""
label_out="roi.nii.gz"

OPTIND=0
while getopts "t:i:l:o:" OPTION
do
	echo "opt $OPTION arg $OPTARG ind $OPTIND"
	case $OPTION in
		i)
			dwi_file=$OPTARG
			;;
		t)	
			tensor_file=$OPTARG
			;;
		l)
			label_file=$OPTARG
			;;
		o)
			label_out=$OPTARG
			;;
		?)
			usage
			exit
			;;
	esac
done

if [ "$dwi_file" != "" ]
then
	echo "DO DWI TO TENSOR"
	touch dti.nhdr
	touch baseline.nhdr
	$cli/DWIToDTIEstimation --shiftNeg -e LS $dwi_file dti.nhdr baseline.nhdr
	tensor_file="dti.nhdr"
	
	$cli/DiffusionTensorScalarMeasurements -e FractionalAnisotropy $tensor_file  FA.nrrd
	$cli/DiffusionTensorScalarMeasurements -e ParallelDiffusivity $tensor_file  AD.nrrd
	$cli/DiffusionTensorScalarMeasurements -e PerpendicularDiffusivity $tensor_file  RD.nrrd
	$cli/ResampleScalarVolume FA.nrrd FA.nii.gz
	$cli/ResampleScalarVolume AD.nrrd AD.nii.gz
	$cli/ResampleScalarVolume RD.nrrd RD.nii.gz	
fi

if [ "$label_file" != "" ]
then
	echo $label_out
	$cli/ResampleScalarVolume -i nearestNeighbor "$label_file" "$label_out"
fi



