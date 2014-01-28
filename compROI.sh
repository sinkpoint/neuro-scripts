#!/bin/bash
#
# Script: CompROI.sh
# Purpose: Computes ROI values based on a ROI mask image, producing a CSV tabular output
# Author:  Thomas Nichols
# Version: $Id: CompROI.sh,v 1.7 2012/11/18 15:08:38 nichols Exp $
# 

# Modified: David Qixiang Chen
# Added ability for different ROIs per image.


###############################################################################
#
# Environment set up
#
###############################################################################

if [ "$FSLDIR" = "" ] ; then
    echo "ERROR: FSLDIR variable not set (FSL required)"
    exit 1
fi
export FSLOUTPUTTYPE=NIFTI
shopt -s nullglob # No-match globbing expands to null
Tmp=/tmp/${$}-

#
# Functions
#_____________________________________________________________________

Usage() {

cat <<EOF
Usage: CompROI.sh [options] roimask roivals ImgTab ROIvalTab

For each image file compute the mean within each ROI specified.

Inputs:
      roimask      Discrete-valued roi image.
      roivals      Space-separated list of values defining rois *or*
                   a text file of values.  Space-separated list (be sure to
                   enclose in quotes) can optionally have text labels 
                   for each roi value (see examples below).  Multiple values
                   separated by plus signs indicate mask formed from a union of
                   multiple values.  Text file of values has a 
                   comma-separated format: first row _must_ be column names; first
                   column are values defining the rois; second column are ROI
                   labels.  Again, values separated by plus signs may also be used.
                   Labels may not contain any spaces.
      ImgTab       Comma-separated table giving image file list; first
                   row _must_ be column names and first column _must_ be
                   unique subject/scan identifiers.  Second column gives
                   full path names of images from which to extract ROI
                   values. (Subsequent columns are ignored.)
Outputs:
      ROIvalTab    Comma-separated table of ROI values.  First column
                   contains the unique subject/scan identifiers, second column
                   the name of the image; subsequent columns are grouped in
                   triplets (though see -meanonly option), first containing
                   the intra-ROI mean, next the intra-ROI standard deviation
                   ('-std') and finally the non-missing voxel count ('-nV').
Options:

      -meanonly    Omit intra-ROI standard deviation and voxel count, creating
                   just column per ROI.

      -lesion THR  Images are (should be) binary, apply a threshold of THR to binarise.
                   Reported values are total lesion volumes (mm^3, what fslstats
                   reports) and no standard deviation or count is given.

Example:
     CompROI.sh ROItemplate "3 4" ImgList.csv Result.csv
Also, can (should) add labels to ROI values with a colon
     CompROI.sh ROItemplate "3:L_Brain 4:R_Brain" ImgList.csv Result.csv
Can merge values into a single ROI
     CompROI.sh ROItemplate "3+4:Brain" ImgList.csv Result.csv
Alternatively, put ROI-defining values in a table
     CompROI.sh ROItemplate ROIlist.csv ImgList.csv Result.csv
EOF
    exit 1
}

SetUp() {

    ok=1

    # Set up the key global variables
    
    IDs=(`awk -F, '{if (NR > 1) print $1}' "$ImgTab"`)
	ROIs=(`awk -F, '{if (NR > 1) print $2}' "$ROITab"`)
    Imgs=(`awk -F, '{if (NR>1) print $2}' "$ImgTab"`)
    nImg=${#Imgs[*]}

    # Parse ROI definition, seting variable nROI, and arrays ROIval and ROIlab
    SetROIdef

    # Some error checking
    
    if [ ${#IDs[*]} -ne ${#Imgs[*]} ] ; then 
		echo "Number of ID's and images in ImgTab don't match"; ok=0; 
    fi


    for(( i=0; i<${#ROIs[*]}; i++)); do
		f="${ROIs[$i]}"
		if [ $(imtest $f) = 0 ] ; 
		then 
			echo "ERROR: ROI image '$f' doesn't exist"; 
			ok=0;
		fi
    done
    

    for (( i=0 ; i<$nImg ; i++ )) ; do
		f=`${FSLDIR}/bin/remove_ext ${Imgs[$i]}`;
		if [ `${FSLDIR}/bin/imtest $f` = 0 ] ; then
	    	printf "ERROR: Missing input image '${Imgs[$i]}'\n"
		    ok=0
		fi
    done

    if [  $ok == 0 ] ; then 
    	echo "# Errors detected, aboard."
		CleanUp
		exit 1
    fi
    echo "# done SetUp"
}

SetROIdef() {
    # Set ROIval & ROIlab arrays
    
    if [ -f "$ROIdef" ] ; 
    then
		ROIval=(`awk -F, '{if (NR>1) print $1}' "$ROIdef"`)
		if [ `awk -F, '{if (NR==2) print $2}' "$ROIdef"` != "" ] ; 
		then
	    	ROIlab=(`awk -F, '{if (NR>1) print $2}' "$ROIdef"`)
		else
	    ROIlab=()
	   	fi
	else
		i=0
	
		for val in $ROIdef ; do
			ROIval[$i]=`echo "$val" | awk -F: '{print $1}'`
			ROIlab[$i]=`echo "$val" | awk -F: '{print $2}'`
			(( i++ ))
		done
    fi
    
    nROI=${#ROIval[*]}

    for (( i=0 ; i<$nROI ; i++ )) ; do
		if [ "${ROIlab[$i]}" == "" ] ; 
		then
	    	ROIlab[$i]=ROI_${ROIval[$i]}
		fi
    done
    
    echo "# done SetROIdef"
}


fslmaths_msk() {
    fslmaths "$@" -odt char 
}

MkROImsks() {

    for (( j=0 ; j<$nROI ; j++ )) ; do 
		vs=${ROIval[$j]}
		new=1
		
		printf ""$vs" "
		
		for v in $(echo $vs | sed 's/+/ /g') ; do
			if [ "$new" == 1 ] ; then
				fslmaths_msk ${ROI} -thr $v -uthr $v -bin ${Tmp}ROI
			else
				fslmaths_msk ${ROI} -thr $v -uthr $v -add ${Tmp}ROI -bin ${Tmp}ROI
			fi
			new=0
		done
		imcp ${Tmp}ROI ${Tmp}ROI-${vs}
    done
    printf "\n"
    
}

WriteHdr() {
    
    awk -F, '{if (NR==1) printf("%s,%s",$1,$2)}' "$ImgTab" > "$ROImeas"
    for (( i=0 ; i<$nROI ; i++ )) ; do
		lab=${ROIlab[$i]}
		echo -n ",${lab}" >> "$ROImeas"
		if (( MeanOnly == 0 && Lesion == 0 )) ; then
			echo -n ",${lab}-std,${lab}-nV" >> "$ROImeas"
		fi
    done
    echo "" >> "$ROImeas"
}


CleanUp() {
    /bin/rm ${Tmp}*
}



#
# Program start
#_____________________________________________________________________



#
# Parse args, check usage
#
MeanOnly=0
Lesion=0
while [ $# -gt 4 ] ; do
    case "$1" in
	-meanonly)
	    MeanOnly=1
	    shift
	    break
	    ;;
	-lesion)
	    Lesion=1
	    shift
	    LesionTh="$1"
	    shift
	    break
	    ;;
	-*)
	    echo "ERROR: Unknown option '$1'"
	    exit 1
	    break
	    ;;
	*)
	    break
	    ;;
    esac
done
if [ $# -lt 4 ] ; then
    Usage
fi

ROITab="$1";
ROIdef="$2"
ImgTab="$3"
ROImeas="$4"; ROImeas=$(dirname "$ROImeas")/$(basename "$ROImeas" .csv).csv

# Check for some errors, and set key variables:
#  nImg, IDs, Imgs, nROI, ROIval, ROIlab
SetUp

#
# Main program
#

# Write header of output table
WriteHdr 

echo ${ROIs[*]}
echo ${Imgs[*]}
echo ${IDs[*]}


for (( i=0 ; i<$nImg ; i++ )) ; do
	echo $i
	# Create ROI masks
	
	f="${Imgs[$i]}"
    echo "Working on $f "
	
	ROI="${ROIs[$i]}"
	echo "ROI: "$ROI""
	echo "Creating nROI=$nROI mask images..."	
	MkROImsks
	echo "."
    
    echo -n "${IDs[$i]},${Imgs[$i]}" >> "$ROImeas"

    for (( r=0 ; r<$nROI ; r++ )) ; do

		val=${ROIval[$r]}
		lab=${ROIlab[$r]}

		printf ""$lab" : "$val" "
	
		if (( Lesion == 0 )) ; then
			# # Original code, without trick:
		        # fslmaths $f -nan -mul ${Tmp}ROI-${val} ${Tmp}wk
		        # Mn=`fslstats ${Tmp}wk -M | sed 's/^[ ]*//;s/[ ]*$//;'`

			# Trick to control the precision reported by fslstats
			fslmaths $f -nan -mul ${Tmp}ROI-${val} -mul 100 ${Tmp}wk -odt float
			Mn=`fslstats ${Tmp}wk -M | sed 's/^[ ]*//;s/[ ]*$//;' | awk '{print $1 / 100 }'`

			echo -n ",$Mn" >> "$ROImeas"

			if (( MeanOnly == 0 )) ; then
				nV=`fslstats ${Tmp}wk -V | awk '{print $1}'`
				Sd=`fslstats ${Tmp}wk -S | sed 's/^[ ]*//;s/[ ]*$//;'`
				echo -n ",$Sd,$nV" >> "$ROImeas"
			fi
		else
			fslmaths_msk $f -nan -mul ${Tmp}ROI-${val} -thr $LesionTh -bin ${Tmp}wk
			Vo=`fslstats ${Tmp}wk -V | awk '{print $2}'`
			echo -n ",$Vo" >> "$ROImeas"
		fi

		echo -n "."

    done
	
    echo "" >> "$ROImeas"
    echo " "

done

CleanUp

exit 0


