import ants
import nibabel as nb
import os
import shutil
import sys
import glob
import pandas as pd
import numpy as np
from subprocess import Popen, DEVNULL, STDOUT, check_call
sys.path.append('/home/mathilde/Documents/scripts/meld_fe_io')
from scripts.coregistration import ants_coregister_to_fixed, ants_coregister_with_transform, correct_bias_n4

def harmonise_bids_name(name):
    split = name.split('_')  
    #change FCD by P
    split = ['P' if x=='FCD' else x for x in split]
    #remove scanner information
    list_exclude = ["3T", "7T", "15T"]
    for l in list_exclude:
        try:
            split.remove(l)
        except:
            pass
    # exclude specific characters
    harmo_name= ''.join(split)
    
    return harmo_name

BIDS_dir = '/media/mathilde/MELD2/MELD2/DATA/MELD_H4/MELD_BIDS'
ref_file_stripped = '/home/mathilde/Documents/scripts/meld_fe_io/data/template/mni_icbm152_t1_tal_nlin_sym_09a_brain.nii'
output_dir = '/media/mathilde/MELD2/MELD2/DATA/MELD_H4/MELD_BIDS_mni'

# load info histo

df = pd.read_csv('/media/mathilde/MELD2/MELD2/DATA/MELD_H4/MELDProjectFocalEpil_REDCAPDATA_H4_230516.csv') 


#define subjects
# subjects = os.listdir(BIDS_dir)
# print(subjects)

#df_include = df[(df['included'].astype('str')=='1.0')&(df['Is this a patient or control?'].astype('str')=='1')].copy()
df_include = df[(df['included']==1)&(df['patient_control']==1)].copy()
subjects_included= np.array(df_include['id'].values)
#subjects_included= np.array(df_include['MELD Project Anonymous Participant ID'].values)



for subject in subjects_included:

    print(subject)
    subject = 'sub-'+harmonise_bids_name(subject)
    output_dir_sub = os.path.join(output_dir,subject)

    #get T1 and lesion mask if exists
    T1_file = glob.glob(os.path.join(BIDS_dir,subject, 'anat','*_preop_T1w.nii.gz'))[0]
    try:
        lesion_mask_file = glob.glob(os.path.join(BIDS_dir,subject, 'anat','*_lesion_mask.nii.gz'))[0]
    except:
        lesion_mask_file = None
        print(f'no lesion mask for subject {subject}')
    
    
    lesion_mask_reg = os.path.join(output_dir_sub,f'{subject}_lesionmask_in_MNI.nii.gz')
    if not os.path.isfile(lesion_mask_reg):
        if lesion_mask_file != None:

            # create folder output subject
            
            os.makedirs(output_dir_sub, exist_ok=True)

            # correct bias T1
            T1_unbias = os.path.join(output_dir_sub,f'{subject}_T1unbias.nii.gz')
            correct_bias_n4(T1_file, T1_unbias)


            # skull strip T1 
            T1_skullstripp = os.path.join(output_dir_sub,f'{subject}_T1brain.nii.gz')
            command = format(f"bet {T1_unbias} {T1_skullstripp}")
            proc = Popen(command, shell=True,)
            proc.wait()

            # Coregister T1 skullstripped to MNI space and save transform
            output_file = os.path.join(output_dir_sub, f'{subject}_T1brain_in_MNI.nii.gz')
            transform_file_base = os.path.join(output_dir_sub,f'{subject}_transform_to_MNI')
            ants_coregister_to_fixed(T1_skullstripp, ref_file_stripped, output_file, save_transform=transform_file_base, transform_type = 'SyN')

            # Coregister T1 using transform
            output_file = os.path.join(output_dir_sub, f'{subject}_T1_in_MNI.nii.gz')
            ants_coregister_with_transform(T1_file, ref_file_stripped, output_file, transform_file_base)

            # Coregister lesion mask using transform
            ants_coregister_with_transform(lesion_mask_file, ref_file_stripped, lesion_mask_reg, transform_file_base)
    else:
        ('Lesion mask registered already exists')
