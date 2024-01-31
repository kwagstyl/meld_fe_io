import os
import glob
import pandas as pd
import numpy as np
import json
import shutil
import matplotlib.pyplot as plt
import argparse
from qc_demographics import qc_demographics

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
    
if __name__ == '__main__':
    # parse commandline arguments
    parser = argparse.ArgumentParser(description="Main pipeline to predict on subject with MELD classifier")
    parser.add_argument("-d","--dir",
                        help="directory with MELD",
                        default=None,
                        required=True,
                        )
    parser.add_argument("-o",
                        "--output_file",
                        help="File to save output",
                        required=True,
                        )
    args = parser.parse_args()
    print(args)

    folder = args.dir
    
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
                demo_qc_array = [0]
                site_array = [site]*len(subject_array)
                note_demos_array = ['Participants infos csv cannot be found']
            elif len(csv)>1:
                print(f'Found multiple participants infos csv for site {site}')
                subject_array = ['all']
                demo_qc_array = [0]
                site_array = [site]
                note_demos_array = ['Found multiple participants infos csv']
            else:
                output_file = csv[0].split('.csv')[0]+'_QC.csv'
                df_qc = qc_demographics(csv[0], site, output_file)
                
                subject_array = df_qc['subject'].values
                demo_qc_array = [1]*len(subject_array)
                site_array = [site]*len(subject_array)
                note_demos_array = df_qc.apply(sum_error, axis=1)
            
            #get the qc of the MRI data
            csv_mri = glob.glob(os.path.join(folder, sub_folder, 'MELD_BIDS_QC', f'df_qc_all_*.csv'))
            
            if len(csv_mri)==0:
                print(f'MRI QC csv cannot be found for site {site}')
                mri_qc_array = [0]*len(subject_array)
                note_mri_array = ['MRI QC csv cannot be found']*len(subject_array)
            elif len(csv_mri)>1:
                print(f'Found multiple MRI QC csv for site {site}')
                mri_qc_array = [0]*len(subject_array)
                note_mri_array = ['Found multiple MRI QC csv']*len(subject_array)
            else:
                df_mri = pd.read_csv(csv_mri[0])
                mri_qc_array = []
                note_mri_array = []
                for subject in subject_array:
                    bids_id = 'sub-'+''.join(subject.split('_'))
                    if not bids_id in df_mri['Subject'].values:
                        mri_qc_array.append(0)
                        note_mri_array.append('QC not done or have failed')
                    else:
                        if int(df_mri[df_mri['Subject']==bids_id]['T1-Preop Correct Mod.'].values[0]) > 0:
                            mri_qc_array.append(1)
                            note_mri_array.append('')
                        else:
                            mri_qc_array.append(0)
                            note_mri_array.append('QC not done')
            
            # print(len(subject_array))
            # print(len(site_array))   
            # print(len(demo_qc_array))   
            # print(len(note_demos_array))      
            # print(len(mri_qc_array)) 
            # print(len(note_mri_array)) 
            df_site = pd.DataFrame(np.array([subject_array, site_array, demo_qc_array, note_demos_array, mri_qc_array, note_mri_array ]).T, columns=['subject', 'site', 'demographic QC (1= complete)','notes demographic QC', 'MRI QC (1=complete)', 'notes MRI QC'])
            
            df_summary = pd.concat([df_summary,df_site])
            
            
    df_summary.to_csv(args.output_file)        

    
    