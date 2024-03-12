import os
import subprocess
import glob
import shutil

folder_orig = '/home/mathilde/Documents/RDS/MELD_FE/DATA/MELD_H16/raw_data/data_meldFCD/MELD_H16'
folder_bids = '/home/mathilde/Documents/RDS/MELD_FE/DATA/MELD_H16/raw_data/data_meldFCD/MELD_H16_filled_2'
subjects = [
                 "MELD_H16_P_0101",
                # "MELD_H16_P_0102",
                # # "MELD_H16_P_0103","MELD_H16_P_0104","MELD_H16_P_0105",
                # #           "MELD_H16_P_0108","MELD_H16_P_0109","MELD_H16_P_0110","MELD_H16_P_0111","MELD_H16_P_0112",
                # #           "MELD_H16_P_0113","MELD_H16_P_0114","MELD_H16_P_0115","MELD_H16_P_0116","MELD_H16_P_0117",
                # #           "MELD_H16_P_0118","MELD_H16_P_0120","MELD_H16_P_0121","MELD_H16_P_0122","MELD_H16_P_0123",
                # #           "MELD_H16_P_0124","MELD_H16_P_0126","MELD_H16_P_0128",
                # #           "MELD_H16_P_0133",
                #           "MELD_H16_P_0134",
                #           "MELD_H16_P_0139",
                #           "MELD_H16_P_0142","MELD_H16_P_0143","MELD_H16_P_0144","MELD_H16_P_0145",
                #           "MELD_H16_P_0148"
                          ] 

for subject in subjects:
    
    subject_bids = 'sub-'+''.join(subject.split('_'))
    t1_fs = os.path.join(folder_bids, subject_bids,'anat', f'{subject_bids}_3T_preop_T1w.nii.gz')   # T1 from freesurfer
    t1_orig = glob.glob(os.path.join(folder_orig, subject,'*.nii'))[0]   ## original T1
    
    # copy T1 orig in bids and zip
    cmnd = f"gzip {t1_orig}"
    try:
        subprocess.run(cmnd.split()) 
    except OSError as e:
        print(f'COMMAND FAILED: {cmnd} with error {e}')
    t1_orig = t1_orig+'.gz'
    t1_orig_bids = os.path.join(folder_bids, subject_bids,'anat', f'{subject_bids}_3T_preop_T1w_orig.nii.gz')
    shutil.copy(t1_orig, t1_orig_bids) 
    
    # #segment orig and t1 freesurfer
    # for file in [t1_orig_bids, t1_fs]:
    #     cmnd = f"mri_synthseg --i {file} --o {folder_bids} --parc --robust"
    #     try:
    #         subprocess.run(cmnd.split()) 
    #     except OSError as e:
    #         print(f'COMMAND FAILED: {cmnd} with error {e}')
    
    #coregister T1 Freesurfer to T1 orig            
    ref = t1_orig_bids
    flo = t1_fs
    ref_seg = t1_orig_bids.split('.nii.gz')[0]+'_synthseg.nii.gz'
    flo_seg = t1_fs.split('.nii.gz')[0]+'_synthseg.nii.gz'
    fwd_field = os.path.join(folder_bids, subject_bids,'anat', 't1fs_to_orig.nii.gz')

    cmnd = f"mri_easyreg --ref {ref} --flo {flo} \
                    --ref_seg {ref_seg} --flo_seg {flo_seg} \
                    --fwd_field {fwd_field} --affine_only"
    try:
        subprocess.run(cmnd.split()) 
    except OSError as e:
        print(f'COMMAND FAILED: {cmnd} with error {e}')
    
    
    # use transformed to coregister t1 and lesion mask into orig
    save_moving_img_pth = t1_fs.split('.nii.gz')[0]+'_coreg.nii.gz'
    cmnd = f"mri_easywarp --i {flo} --o {save_moving_img_pth} \
            --field {fwd_field} --nearest"
    try:
        subprocess.run(cmnd.split())  
    except OSError as e:
        print(f'COMMAND FAILED: {cmnd} with error {e}')
    
    lesion = os.path.join(folder_bids, subject_bids,'anat', f'{subject_bids}_3T_lesion_mask_filled.nii.gz')
    save_moving_lesion_pth = lesion.split('.nii.gz')[0]+'_coreg.nii.gz'
    cmnd = f"mri_easywarp --i {lesion} --o {save_moving_lesion_pth} \
            --field {fwd_field} --nearest"
    try:
        subprocess.run(cmnd.split())  # all extras saved to synth_sr_folder
    except OSError as e:
        print(f'COMMAND FAILED: {cmnd} with error {e}')
    
    