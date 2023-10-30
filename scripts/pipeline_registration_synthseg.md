# Pipeline to run registration with SynthSeg



## source & installation 
Install Freesurfer V7.4 for mri_easyreg and synthseg (https://surfer.nmr.mgh.harvard.edu/fswiki/SynthSeg)


## initialisation
input_folder :  should be taken from the MELD_BIDS folder\
output_folder:  should be strored in QC folder

## Register any modality 

1. if modality is post-op do preliminary step, otherwise go to step 2
```bash
 mri_synthsr --i '<input_folder>/<subject>/anat/<subject>_3T_postop_T1w.nii.gz' --o 'output_folder/synthseg/'
```

2. Run synthseg to segment T1 and the modalities (e.g FLAIR). If modality is postop input should be result of step 1

```bash
mri_synthseg --i '<input_folder>/<subject>/anat/<subject>_3T_preop_T1w.nii.gz' --o 'output_folder/synthseg/' --parc --vol 'output_folder/synthseg/<subject>_3T_preop_T1w_vol.csv'
mri_synthseg --i '<input_folder>/<subject>/anat/<subject>_3T_preop_FLAIR.nii.gz' --o 'output_folder/synthseg/' --parc --vol 'output_folder/synthseg/<subject>_3T_preop_FLAIR_vol.csv'
```

Note: can parallelise with a single command where \
-i is a txt file where each line is the path of an image to segment \
-o is a txt file where each line is the path to an output segmentation \
-vol is a txt file, where each line is the path to a different CSV file where the volumes of the corresponding subject will be saved \

3. Run mri_easyreg to register each modality to T1
```bash
mri_easyreg --ref '<input_folder>/<subject>/anat/<subject>_3T_preop_T1w.nii.gz' 
            --flo '<input_folder>/<subject>/anat/<subject>_3T_preop_FLAIR.nii.gz' 
            --ref_seg '<output_folder>/synthseg/<subject>_3T_preop_T1w_synthseg.nii.gz' 
            --flo_seg '<output_folder>/synthseg/<subject>_3T_preop_FLAIR_synthseg.nii.gz' 
            --fwd_field '<output_folder>/synthseg/<subject>_3T_preop_FLAIR_T1_fwdfield.nii.gz' 
```

4. Apply forward field to each modality and save registered modality in output folder
```bash
mri_easywarp --i '<input_folder>/<subject>/anat/<subject>_3T_preop_FLAIR.nii.gz' --o '<output_folder>/MELD_BIDS_reg/<subject>/anat/<subject>_3T_preop_FLAIR.nii.gz' --field '<output_folder>/synthseg/<subject>_3T_preop_FLAIR_T1_fwdfield.nii.gz' --nearest
```


