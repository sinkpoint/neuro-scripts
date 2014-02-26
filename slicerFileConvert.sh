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

in_file=""
out_file=""

OPTIND=0
while getopts "i:o:" OPTION
do
	echo "opt $OPTION arg $OPTARG ind $OPTIND"
	case $OPTION in
		i)
			in_file=$OPTARG
			;;
		o)
			out_file=$OPTARG
			;;
		?)
			usage
			exit
			;;
	esac
done

if [ "$in_file" != "" ]
then
	echo "DO Conversion"
	$cli/ResampleScalarVolume $in_file $out_file
fi
