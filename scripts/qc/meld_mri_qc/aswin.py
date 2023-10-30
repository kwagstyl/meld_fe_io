#!/bin/bash

#export ANTSPATH=/opt/ANTs/bin/
#export PATH=${ANTSPATH}:$PATH

#for sub in sub-11; do

	# forward

#	fslmaths $sub/resection.nii.gz -mul -1 -add 1 -bin $sub/resection_inv.nii.gz

#	antsRegistrationSyNQuick.sh -d 3 -m $sub/t1_reg.nii.gz -f $sub/postop.nii.gz -t s -o $sub/output -x $sub/resection_inv.nii.gz

	# inverse

#	antsApplyTransforms -d 3 -i $sub/postop.nii.gz -r $sub/t1_reg.nii.gz -t [$sub/output0GenericAffine.mat, 1] -t $sub/output1InverseWarp.nii.gz -o $sub/postop_reg.nii.gz

#	antsApplyTransforms -d 3 -i $sub/resection.nii.gz -r $sub/t1_reg.nii.gz -t [$sub/output0GenericAffine.mat, 1] -t $sub/output1InverseWarp.nii.gz -o $sub/resection_reg.nii.gz  -n NearestNeighbor

#done

