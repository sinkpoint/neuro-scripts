#!/bin/bash

usage()
{
	cat<<EOF
	usage: $0 options arg
	
	OPTIONS:
		-i		input dwi file
		-t		output tensor file, default is dti.nhdr
		-d 		output directory
		-p 		output file prefix
		-l		input label file, will convert this file with nearest-neighbour
		-o		output label file
		-? 		help
	
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
while getopts "i:t:d:p:l:o:" OPTION
do
	echo "opt $OPTION arg $OPTARG ind $OPTIND"
	case $OPTION in
		i)
			dwi_file=$OPTARG
			;;
		t)	
			tensor_file=$OPTARG
			;;
		d)  
			output_dir=$OPTARG
			;;
		p)
			prefix=$OPTARG
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

if [ -z "$output_dir" ]
then
	output_dir=`pwd`
fi
echo "Output to "$output_dir""

if [ $OPTIND -eq 1 ]
then
	usage
	exit
fi

if [ -z "$dwi_file" ] && [ -z "$label_file" ]
then
	usage
	exit
fi

if [ -z "$tensor_file" ]
then
	tensor_file="dti.nhdr"
fi

tensor_file="$output_dir/$prefix$tensor_file"
baseline_base="$output_dir/${prefix}baseline"
baseline_file="$baseline_base.nrrd"

if [ -n "$dwi_file" ]
then
	echo "DO DWI TO TENSOR"
	touch $tensor_file
	touch $baseline_file
	$cli/DWIToDTIEstimation --shiftNeg -e LS $dwi_file $tensor_file $baseline_file
	
	$cli/DiffusionTensorScalarMeasurements -e FractionalAnisotropy $tensor_file  "$output_dir"/${prefix}FA.nrrd
	$cli/DiffusionTensorScalarMeasurements -e ParallelDiffusivity $tensor_file  "$output_dir"/${prefix}AD.nrrd
	$cli/DiffusionTensorScalarMeasurements -e PerpendicularDiffusivity $tensor_file  "$output_dir"/${prefix}RD.nrrd
	
	$cli/ResampleScalarVolume "$baseline_file" "$baseline_base.nii.gz"
	$cli/ResampleScalarVolume "$output_dir"/${prefix}FA.nrrd "$output_dir"/${prefix}FA.nii.gz
	$cli/ResampleScalarVolume "$output_dir"/${prefix}AD.nrrd "$output_dir"/${prefix}AD.nii.gz
	$cli/ResampleScalarVolume "$output_dir"/${prefix}RD.nrrd "$output_dir"/${prefix}RD.nii.gz	
fi

if [ -n "$label_file" ]
then
	echo $label_out
	$cli/ResampleScalarVolume -i nearestNeighbor "$label_file" "$output_dir/${prefix}$label_out"
fi



