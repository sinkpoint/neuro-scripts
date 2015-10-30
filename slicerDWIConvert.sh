#!/bin/bash

cli=$SLICER4_HOME/lib/Slicer-4.3/cli-modules
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$SLICER4_HOME/lib/Slicer-4.3:$LD_LIBRARY_PATH:$SLICER4_HOME/lib/Slicer-4.3/cli-modules:$SLICER4_HOME/lib/Teem-1.10.0

args=("$@")
# if [ -z $args ]; then
# 	usage
# 	exit
# fi

$cli/DWIConvert $@

