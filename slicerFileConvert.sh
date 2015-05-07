#!/bin/bash

usage()
{
	cat<<EOF
	usage: $0 options arg
	
	OPTIONS:
		-i <input file>
		-o <output file>
	
EOF
}

cli=$SLICER4_HOME/lib/Slicer-4.3/cli-modules
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$SLICER4_HOME/lib/Slicer-4.3:$LD_LIBRARY_PATH:$SLICER4_HOME/lib/Slicer-4.3/cli-modules:$SLICER4_HOME/lib/Teem-1.10.0

args=("$@")
if [ -z $args ]; then
	usage
	exit
fi

in_file=""
out_file=""

OPTIND=0
while getopts "i:o:" OPTION
do
	case $OPTION in
		i)
			in_file=$OPTARG
			;;
		o)
			out_file=$OPTARG
			;;
	esac
done


	$cli/ResampleScalarVolume $@

