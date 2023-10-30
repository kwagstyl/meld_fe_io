# Pipeline to run registration with SynthSeg



### source & installation 
Install Freesurfer V7.4 for mri_easyreg and synthseg (https://surfer.nmr.mgh.harvard.edu/fswiki/SynthSeg)


### initialisation
input_folder :  should be taken from the MELD_BIDS folder
output_folder:  should be strored in QC/synthseg or QC/MELD_BIDS_reg folders

### Register any modality - except post-op

1. Run synthseg to segment T1 and the modalities (e.g FLAIR)

```bash
mri_synthseg --i '<input_folder>/<subject>/anat/<subject>_3T_preop_T1w.nii.gz' --o '/synthseg' --parc --vol '/synthseg/<subject>_3T_preop_T1w_vol.csv'
mri_synthseg --i '<input_folder>/<subject>/anat/<subject>_3T_preop_FLAIR.nii.gz' --o '/synthseg' --parc --vol '/synthseg/<subject>_3T_preop_FLAIR_vol.csv'
```

Note: can parallelise with a single command where \
-i is a txt file where each line is the path of an image to segment \
-o is a txt file where each line is the path to an output segmentation \
-vol is a txt file, where each line is the path to a different CSV file where the volumes of the corresponding subject will be saved \

2. Run mri_easyreg to register each modality to T1
```bash
mri_easyreg --ref '<input_folder>/<subject>/anat/<subject>_3T_preop_T1w.nii.gz' 
            --flo '<input_folder>/<subject>/anat/<subject>_3T_preop_FLAIR.nii.gz' 
            --ref_seg '/synthseg/<subject>_3T_preop_T1w_synthseg.nii.gz' 
            --flo_seg '/synthseg/<subject>_3T_preop_FLAIR_synthseg.nii.gz' 
            --fwd_field '/synthseg/<subject>_3T_preop_FLAIR_T1_fwdfield.nii.gz' 
```

3. Apply forward field to each modality and save registered modality in output folder
```bash
mri_easywarp --i '<input_folder>/<subject>/anat/<subject>_3T_preop_FLAIR.nii.gz' --o <output_folder>/<subject>/anat/<subject>_3T_preop_FLAIR.nii.gz --field '/synthseg/<subject>_3T_preop_FLAIR_T1_fwdfield.nii.gz' --nearest
```


