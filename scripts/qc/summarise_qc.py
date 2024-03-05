import os
import glob
import pandas as pd
import numpy as np
import json
import shutil
import matplotlib.pyplot as plt
import argparse
from meld_demo_qc.qc_demographics import qc_demographics

columns = ['id', 'site', 'patient_control', 'sex',
       'radiology', 'radiology_report', 'field_strengths___1',
       'field_strengths___2', 'field_strengths___3', 'age_at_preop_t1_15t',
       'age_at_preop_t1_3t', 'age_at_preop_t1_7t', 'preop_t1_yr_15t',
       'preop_t1_yr_3t', 'preop_t1_yr_7t', 'postop_t1_yr',
       'postop_t1_yr_2___1', 'postop_t1_yr_2___2', 'postop_t1_yr_2___3',
       'control_headache', 'preop_t1', 'preop_t2', 'preop_flair', 'preop_dwi',
       'postop_t1', 'fields', 'lesion_mask', 'age_at_onset', 'gtcs',
       'drug_resistant', 'aeds', 'mri_negative', 'seeg', 'operated',
       'surgery_year', 'age_at_surgery', 'mri_negative_surgery', 'procedure',
       'procedure_other', 'histology', 'histology_other', 'seizure_free',
       'seizure_free_aura', 'engel_1yr', 'ilae_1yr', 'engel', 'ilae',
       'follow_up', 'aeds_post_op', 'participant_information_complete']


def check_mod_qc(values, mod):
    # values = T1-Preop Correct Mod.	T1-Preop Artefact	T1-Preop FOV	T1-Preop Defacing
    error = ""
    return_code = 1
    if int(values[0])==2:
        return_code = 0
        error = error + f'Error with {mod} scan: not the right modality;'
        return return_code, error
    if int(values[0])==3:
        return_code = 0
        error = error + f'Error with {mod} scan: contrast agent;'
        return return_code, error
    if int(values[0])==4:
        return_code = 0
        error = error + f'Error with {mod} scan: possible previous resection;'
        return return_code, error
    if int(values[0])==5:
        return_code = 0
        error = error + f'Error with {mod} scan: cannot see resection;'
        return return_code, error
    if int(values[0])==6:
        return_code = 0
        error = error + f'Error with {mod} scan: problem with opening file;'
        return return_code, error
    if int(values[0])==1:
        if int(values[1])==3:
            return_code = 0
            error = error + f'Strong artefact on {mod};'
        # if int(values[2])>1:
        #     return_code = 0
        #     error = error + f'FOV cropped on {mod};'
        if int(values[3])==2:
            return_code = 0
            error = error + f'Defacing error: Face remaining on {mod};'
        elif int(values[3])>2:
            return_code = 0
            error = error + f'Defacing error: Part of brain removed on {mod};'
    return return_code, error


def sum_error(row):
    notes = ''
    for column in columns:
        try:
            if row[column+'.passcheck']==0:
                error = row[column+'.error']
                notes = notes + f'error in {column}: {error} ;'
        except:
            pass

    return notes   

def color_dataframe(row):
    if row['demographic QC (1= complete)']==0:
        color = 'yellow'
    elif row['MRI QC (1=complete)']==0:
        color = 'lightcoral'
    elif row['T1-Preop QC (0=to discard, 1=usable)']==0:
        color = 'lightcoral'
    elif row['mask QC ( 0=not correct, 1=correct , 2= seem correct but no postop to check, 3= mask missing, 4=mask required, 5=mask is resection cavity)']==0:
        color = 'lightcoral'
    elif row['mask QC ( 0=not correct, 1=correct , 2= seem correct but no postop to check, 3= mask missing, 4=mask required, 5=mask is resection cavity)']==3:
        color = 'yellow'
    elif row['mask QC ( 0=not correct, 1=correct , 2= seem correct but no postop to check, 3= mask missing, 4=mask required, 5=mask is resection cavity)']==4:
        color = 'lightcoral'
    elif (row['FLAIR QC (0=to discard, 1=usable)']==0) or (row['T2 QC (0=to discard, 1=usable)']==0) or (row['T1-Postop QC (0=to discard, 1=usable)']==0):
        color = 'yellow'
    else: 
        color = 'lightgreen'
        
    return [f'background-color: {color}'] * len(row) 
            
if __name__ == '__main__':
    # parse commandline arguments
    parser = argparse.ArgumentParser(description="Main pipeline to predict on subject with MELD classifier")
    parser.add_argument("-d","--dir",
                        help="directory with MELD",
                        default=None,
                        required=True,
                        )
    parser.add_argument("-site","--site",
                        help="specific site ",
                        default=None,
                        required=False,
                        )
    parser.add_argument("-o",
                        "--output_file",
                        help="File to save output",
                        required=True,
                        )
    args = parser.parse_args()
    print(args)

    folder = args.dir
    
    if not args.site is None:
        site = args.site 
        sub_folders = [f"MELD_{site}"]
    else:
        # get all the sites
        sub_folders = os.listdir(folder)
    
    
    df_summary = pd.DataFrame()
    for sub_folder in sub_folders:
        print(sub_folder)
        if 'MELD_H' in sub_folder:
            site = sub_folder.split('MELD_')[-1]
            
            #get the qc of the demographic
            csv = [file for file in glob.glob(os.path.join(folder, sub_folder, f'MELD_participants_infos_{site}_*.csv')) if 'QC' not in file]
            if len(csv)==0:
                print(f'Participants infos csv cannot be found for site {site}')
                subject_array = ['all']
                original_subject_array = ['']
                demo_qc_array = [0]
                site_array = [site]*len(subject_array)
                note_demos_array = ['Participants infos csv cannot be found']
            elif len(csv)>1:
                print(f'Found multiple participants infos csv for site {site}')
                subject_array = ['all']
                original_subject_array = ['']
                demo_qc_array = [0]
                site_array = [site]
                note_demos_array = ['Found multiple participants infos csv']
            else:
                output_file = csv[0].split('.csv')[0]+'_QC.csv'
                df_qc = qc_demographics(csv[0], site, output_file)
                subject_array = df_qc['study ID'].values
                original_subject_array = df_qc['original ID given by site'].values
                site_array = [site]*len(subject_array)
                note_demos_array =  df_qc.apply(sum_error, axis=1)
                demo_qc_array = [1 if note=='' else 0 for note in note_demos_array]
            
            #get the qc of the MRI data
            csv_mri = glob.glob(os.path.join(folder, sub_folder, 'MELD_BIDS_QC', f'df_qc_all_*.csv'))
            
            mods=['T1-Preop','FLAIR', 'T2', 'T1-Postop']
            mod_qc_correct = {'T1-Preop':[],'FLAIR':[], 'T2':[], 'T1-Postop':[]}
            if len(csv_mri)==1:
                df_mri = pd.read_csv(csv_mri[0])
                mri_qc_array = []
                note_mri_array = []
                mask_qc_correct = []
                for subject in subject_array:
                    bids_id = 'sub-'+''.join(subject.split('_'))
                    if not bids_id in df_mri['Subject'].values:
                        mri_qc_array.append(0)
                        note_mri_array.append('QC not done or have failed')
                        [mod_qc_correct[mod].append(np.nan) for mod in mods]
                        mask_qc_correct.append(np.nan)
                    else:
                        if df_mri[df_mri['Subject']==bids_id]['T1-Preop Correct Mod.'].values[0] is np.nan:
                            mri_qc_array.append(0)
                            note_mri_array.append('QC not done')
                            [mod_qc_correct[mod].append(np.nan) for mod in mods]
                            mask_qc_correct.append(np.nan)
                        else:
                            mri_qc_array.append(1)
                            note_mri=''
                            #check modalities
                            for mod in mods :
                                if int(df_mri[df_mri['Subject']==bids_id][f'{mod} Present'].values[0])==1:
                                    return_code, error = check_mod_qc(df_mri[df_mri['Subject']==bids_id][[f'{mod} Correct Mod.',f'{mod} Artefact',f'{mod} FOV',f'{mod} Defacing']].values[0], mod)
                                    if return_code == 0:
                                        mod_qc_correct[mod].append(0)
                                        note_mri = note_mri + ';' + error
                                    else:
                                        mod_qc_correct[mod].append(1)
                                else:
                                    mod_qc_correct[mod].append(np.nan)
                            #check lesion mask
                            if int(df_mri[df_mri['Subject']==bids_id]['Mask Present'].values[0])==0:
                                if df_qc[df_qc['study ID']==subject]['need_mask'].values[0]==1:
                                    if mod_qc_correct['T1-Postop'][-1]==1:
                                        note_mri = note_mri + ';' + 'mask missing. If not provided, postop will be used as ground truth, but for evaluation only'
                                        mask_qc_correct.append(3)
                                    else:
                                        note_mri = note_mri + ';' + 'mask needed. Patient cannot be included as no ground truth is provided'
                                        mask_qc_correct.append(4)                                        
                                else:
                                    mask_qc_correct.append(np.nan)
                            else:
                                if df_mri[df_mri['Subject']==bids_id]['Mask QC'].values[0] is np.nan: 
                                    mask_qc_correct.append(0)
                                    note_mri = note_mri + ';' + 'mask present but not QCed'
                                elif int(df_mri[df_mri['Subject']==bids_id]['Mask QC'].values[0])==1: 
                                    mask_qc_correct.append(1)
                                elif int(df_mri[df_mri['Subject']==bids_id]['Mask QC'].values[0])==2: 
                                    mask_qc_correct.append(2)
                                elif int(df_mri[df_mri['Subject']==bids_id]['Mask QC'].values[0])==6: 
                                    mask_qc_correct.append(5)
                                    note_mri = note_mri + ';' + 'mask is resection cavity' 
                                elif int(df_mri[df_mri['Subject']==bids_id]['Mask QC'].values[0])>2: 
                                    mask_qc_correct.append(0)
                                    note_mri = note_mri + ';' + 'Error with mask'     
                            note_mri_array.append(note_mri)
            else:   
                mri_qc_array = [0]*len(subject_array)
                for mod in mods:
                    mod_qc_correct[mod] = [np.nan]*len(subject_array)
                mask_qc_correct = [np.nan]*len(subject_array)
                if len(csv_mri)==0:
                    note_mri_array = ['MRI QC csv cannot be found']*len(subject_array)
                    print(f'MRI QC csv cannot be found for site {site}')
                else:
                    print(f'Found multiple MRI QC csv for site {site}')             
                    note_mri_array = ['Found multiple MRI QC csv']*len(subject_array)

            df_site = pd.DataFrame(np.array([subject_array, original_subject_array, site_array, demo_qc_array, note_demos_array, mri_qc_array, mod_qc_correct['T1-Preop'], mod_qc_correct['FLAIR'], mod_qc_correct['T2'], mod_qc_correct['T1-Postop'], mask_qc_correct, note_mri_array ]).T, 
                                   columns=['study ID', 'original ID given by site', 'site', 'demographic QC (1= complete)','notes demographic QC', 'MRI QC (1=complete)',
                                            'T1-Preop QC (0=to discard, 1=usable)', 'FLAIR QC (0=to discard, 1=usable)', 'T2 QC (0=to discard, 1=usable)', 'T1-Postop QC (0=to discard, 1=usable)', 
                                            'mask QC ( 0=not correct, 1=correct , 2= seem correct but no postop to check, 3= mask missing, 4=mask required, 5=mask is resection cavity)', 'notes MRI QC' ])
            
            df_summary = pd.concat([df_summary,df_site])
    
    df_summary = df_summary.reset_index()
    df_summary.to_csv(args.output_file)
            
    # Apply conditional formatting
    styled_df = df_summary.style.apply(color_dataframe,  axis=1)
    # Save to CSV with conditional formatting  
    excel_file = args.output_file.split('.csv')[0]+'.xlsx'
    styled_df.to_excel(excel_file, engine='openpyxl', index=False)       

    
    
