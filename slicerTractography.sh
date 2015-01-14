#!/bin/bash


cli=$SLICER3_HOME/lib/Slicer3/Plugins
SLICER_LIB=$SLICER3_HOME/lib

for d in $(find $SLICER_LIB -maxdepth 2 -type d); do
	export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$d
done

export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$cli

$cli/Seeding $@
