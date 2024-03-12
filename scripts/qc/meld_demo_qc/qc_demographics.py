import os
import glob
import pandas as pd
import numpy as np
import json
import shutil
import matplotlib.pyplot as plt
import argparse


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

def initialise_function(site_code):
    check_functions = {
        'id':                   (lambda x: check_id_MELD(x, 
                                                    site_code=site_code)),
        'site':                 (lambda x: check_site_code(x, 
                                                    site_code=site_code)),
        'patient_control':      (lambda x: check_in_categories(x, 
                                                    categories=[1,2])),
        'sex':                  (lambda x: check_in_categories(x, 
                                                    categories=[0,1])),
        'radiology':            (lambda x: check_in_categories(x, 
                                                    categories=[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,21,22,23])), 

        'field_strengths___1':  (lambda x: check_in_categories(x, categories=[0,1])),
        'field_strengths___2':  (lambda x: check_in_categories(x, categories=[0,1])),
        'field_strengths___3':  (lambda x: check_in_categories(x, categories=[0,1])),

        'age_at_preop_t1_15t':  (lambda x: check_age_years(x)),
        'age_at_preop_t1_3t':   (lambda x: check_age_years(x)), 
        'age_at_preop_t1_7t':   (lambda x: check_age_years(x)),

        'preop_t1_yr_15t':      (lambda x: check_year(x)),
        'preop_t1_yr_3t':       (lambda x: check_year(x)),
        'preop_t1_yr_7t':       (lambda x: check_year(x)), 
        'postop_t1_yr':         (lambda x: check_year(x)),
        'postop_t1_yr_2___1':   (lambda x: check_in_categories(x, categories=[0,1])),
        'postop_t1_yr_2___2':   (lambda x: check_in_categories(x, categories=[0,1])),
        'postop_t1_yr_2___3':   (lambda x: check_in_categories(x, categories=[0,1])),

        'control_headache':     (lambda x: check_in_categories(x, 
                                                    categories=[1,2,555])),

        'preop_t1':             (lambda x: check_in_categories(x, categories=[0,1])), 
        'preop_t2':             (lambda x: check_in_categories(x, categories=[0,1])),
        'preop_flair':          (lambda x: check_in_categories(x, categories=[0,1])), 
        'preop_dwi':            (lambda x: check_in_categories(x, categories=[0,1])),
        'postop_t1':            (lambda x: check_in_categories(x, categories=[1,2,3])),
        'fields':               (lambda x: check_in_categories(x, categories=[0,1])),
        'lesion_mask':          (lambda x: check_in_categories(x, 
                                                    categories=[0,1,555])),
        'age_at_onset':         (lambda x: check_age_years(x)),
        
        'gtcs':                 (lambda x: check_in_categories(x, 
                                                    categories=[0,1,3])),
        'drug_resistant':       (lambda x: check_in_categories(x, 
                                                    categories=[0,1,3])),
        # 'aeds': str,
        
        'mri_negative':         (lambda x: check_in_categories(x, 
                                                    categories=[0,1,3])),
        'seeg':                 (lambda x: check_in_categories(x, 
                                                    categories=[0,1,3])),
        'operated':             (lambda x: check_in_categories(x, 
                                                    categories=[0,1,3])),
        'surgery_year':         (lambda x: check_year(x)),
        
        'age_at_surgery':       (lambda x: check_age_years(x)),

        'mri_negative_surgery': (lambda x: check_in_categories(x, 
                                                    categories=[0,1,555])),
        'procedure':            (lambda x: check_in_categories(x, 
                                                    categories=[1,2,3,4,555])),
                            
        # 'procedure_other',

        'histology':            (lambda x: check_in_categories(x, 
                                                    categories=[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,21,22,23])),
        # 'histology_other'
        
        'seizure_free':         (lambda x: check_in_categories(x, 
                                                    categories=[1,2,555])),
        'seizure_free_aura':    (lambda x: check_in_categories(x, 
                                                    categories=[1,2,555])),
        'engel_1yr':            (lambda x: check_in_categories(x, 
                                                    categories=[1,2,3,4,555])),
        'ilae_1yr':             (lambda x: check_in_categories(x, 
                                                    categories=[1,2,3,4,5,6,555])),
        'engel':                (lambda x: check_in_categories(x, 
                                                    categories=[1,2,3,4,5,6,555])),
        'ilae' :                (lambda x: check_in_categories(x, 
                                                    categories=[1,2,3,4,5,6,555])),
        'aeds_post_op':         (lambda x: check_in_categories(x, 
                                                    categories=[1,2,3,555])),
        'follow_up':         (lambda x: check_age_years(x, range=[0,20])),
    }
    return check_functions

def is_nan(x):
    return (x != x)

def check_id_MELD(value, site_code):
    parts = value.split("_")
    error = ""
    return_code = 1
    if len(parts)!=4:
        return_code = 0
        error = error + 'Error in MELD id structure;'
        return return_code, error
    if parts[0] != 'MELD':
        return_code = 0
        error + 'Error in first term of the id structure;'
    if parts[1]!=site_code:
        return_code = 0
        error = error + 'Wrong site code;'
    if not (parts[2] == 'C') and not (parts[2] == 'P'):
        return_code = 0
        error = error + 'Error in group, other than C or P;'
    return return_code, error

def check_site_code(value, site_code):
    error = ""
    return_code = 1
    if value!=site_code:
        return_code = 0
        error = error + 'Wrong site code;'
    return return_code, error

def check_in_categories(value, categories):
    valid_values = set(categories)
    error = ""
    return_code = 1
    if not is_nan(value):
        if not value in valid_values:
            return_code = 0
            error = error + f'Value {value} not in allowed categories;'
    return return_code, error 

def check_age_years(value, range=[0,80]):
    error = ""
    return_code = 1
    if not is_nan(value):
        if value==555:
            return_code = 2
            error = error + f'Value {value} seems to be months instead of years;'
        elif not (value>range[0]) or not (value<range[1]):
            return_code = 0
            error = error + f'Value {value} seems to be months instead of years;'
        else:
            pass
    return return_code, error 


def check_year(value, range=[2000,2025]):
    error = ""
    return_code = 1
    if not is_nan(value):
        if value==555:
            return_code = 2
        elif not (value>range[0]) or not (value<range[1]):
            return_code = 0
            error = error + f'Value {value} seems to be a wrong year;'
        else:
            pass
    return return_code, error 



def qc_demographics(csv_file, site_code, output_file):
    '''
    # check values in column and create a csv with qc summary
    # return 0 if there is an error, 1 if correct and 2 if missing
    # print freetext for certain categories
    '''
    df_raw=pd.read_csv(csv_file, index_col=None)
    #take only included
    # df = df_raw.copy()
    df = df_raw[df_raw['included'] ==1].copy()
    df.head()

    #initialise qc dataframe
    df_qc = pd.DataFrame()

    #initialise function
    check_functions = initialise_function(site_code)

    for i, df_row in df.iterrows():
        values={}
        values['study ID']=df_row['id']
        values['original ID given by site']=df_row['old_id']
        for column in columns:
            value = df_row[column]
            if column in check_functions:
                if is_nan(value):
                    values[column+'.passcheck']=2
                    values[column+'.error']=''
                else:
                    error_code, error = check_functions[column](value)
                    values[column+'.passcheck']=error_code
                    if error_code==0 :
                        values[column+'.error']=error
                    else:
                        values[column+'.error']=''
            elif column in ['radiology_report', 'aeds', 'procedure_other', 'histology_other']:
                if is_nan(value):
                    values[column+'.passcheck']=2
                    values[column+'.text']=''
                else:
                    values[column+'.passcheck']=1
                    values[column+'.text']=value
        df_qc = pd.concat([df_qc, pd.DataFrame([values])])
    df_qc = df_qc.reset_index(drop=True)
    df_qc.head()

    ### check mandatory data are provided

    # combine age preop t1
    df['age_at_preop_t1'] = df['age_at_preop_t1_3t']
    df['age_at_preop_t1'] = df['age_at_preop_t1'].fillna(df['age_at_preop_t1_7t'])
    df['age_at_preop_t1'] = df['age_at_preop_t1'].fillna(df['age_at_preop_t1_15t'])


    # check mandatory data are given and correct

    for i,df_row in df.iterrows():
        values = {}
        subject=df_row['id']
        # check id, group and sex provided
        for key in ['id', 'sex', 'patient_control']:
            # check id provided
            test = not is_nan(df_row[key])
            # update code and error
            if test == True:
                pass
            else:
                error_code, error = df_qc[df_qc['study ID']==subject][[f'{key}.passcheck',f'{key}.error']].values[0]
                df_qc.loc[df_qc['study ID'] == subject, f'{key}.passcheck'] = 0
                df_qc.loc[df_qc['study ID'] == subject, f'{key}.error'] = error +'This is a mandatory information;'
        
        # check preop age provided
        test = not is_nan(df_row['age_at_preop_t1'])
        if test==True:
            pass
        else:
            for key in ['age_at_preop_t1_3t', 'age_at_preop_t1_7t', 'age_at_preop_t1_15t']:
                error_code, error = df_qc[df_qc['study ID']==subject][[f'{key}.passcheck',f'{key}.error']].values[0]
                df_qc.loc[df_qc['study ID'] == subject, f'{key}.passcheck'] = 0
                df_qc.loc[df_qc['study ID'] == subject, f'{key}.error'] = error +'Age at preoperative is a mandatory information;'

        # only mandatory for patients
        if df_row['patient_control']==1:
            # check age of onset provided and smaller than preop
            key= 'age_at_onset'
            test = (not is_nan(df_row[key])) and (not df_row[key]==555)
            if test == True:
                # test if age of onset younger than age at preop
                test = (df_row['age_at_onset']<=df_row['age_at_preop_t1'])
                # update code and error
                if test == True:
                    pass
                else:
                    error_code, error = df_qc[df_qc['study ID']==subject][[f'{key}.passcheck',f'{key}.error']].values[0]
                    df_qc.loc[df_qc['study ID'] == subject, f'{key}.passcheck'] = 0
                    df_qc.loc[df_qc['study ID'] == subject, f'{key}.error'] = error +'Age of onset older than age at preop;'
            else:
                error_code, error = df_qc[df_qc['study ID']==subject][[f'{key}.passcheck',f'{key}.error']].values[0]
                df_qc.loc[df_qc['study ID'] == subject, f'{key}.passcheck'] = 0
                df_qc.loc[df_qc['study ID'] == subject, f'{key}.error'] = error +'This is a mandatory information;'
            
            # check radiology or histology provided
            test = (not is_nan(df_row['radiology'])) or (not is_nan(df_row['histology']))
            if test==True:
                pass
            else:
                for key in ['radiology', 'histology']:
                    error_code, error = df_qc[df_qc['study ID']==subject][[f'{key}.passcheck',f'{key}.error']].values[0]
                    df_qc.loc[df_qc['study ID'] == subject, f'{key}.passcheck'] = 0
                    df_qc.loc[df_qc['study ID'] == subject, f'{key}.error'] = error +'Radiology or Histology are mandatory information;'  

            # check if lesion mask / postop needed (if not HS)
            if not is_nan(df_row['histology']):
                if df_row['histology']==10:
                    df_qc.loc[df_qc['study ID'] == subject, f'need_mask'] = 0
                else:
                    df_qc.loc[df_qc['study ID'] == subject, f'need_mask'] = 1
            else:
                df_qc.loc[df_qc['study ID'] == subject, f'need_mask'] = np.nan
        else:
            df_qc.loc[df_qc['study ID'] == subject, f'need_mask'] = 0
                
    # save matrix 
    df_qc.to_csv(output_file)
    print(f'QC matrix saved at {output_file}')

    return df_qc
    

if __name__ == '__main__':
    # parse commandline arguments
    parser = argparse.ArgumentParser(description="Main pipeline to predict on subject with MELD classifier")
    parser.add_argument("-f","--file",
                        help="demographic file to qc",
                        default=None,
                        required=True,
                        )
    parser.add_argument("-site",
                        "--site",
                        help="Site code",
                        required=True,
                        )
    parser.add_argument("-o",
                        "--output_file",
                        help="File to save output",
                        required=True,
                        )
    args = parser.parse_args()
    print(args)

    # initialise 
    site_code = args.site
    
    csv_file = args.file
 
    output_file = args.output_file

    df_qc = qc_demographics(csv_file, site_code, output_file)
    
    #print errors 
    # for each columns print subject with error and the error
    for column in columns:
        try:
            if (df_qc[column+'.passcheck']==0).any():
                print(f"Error found in column {column}")
                failed_row = df_qc.loc[df_qc[column+'.passcheck']==0].index
                print(f"subjects: {df_qc.loc[failed_row, 'subject'].values}")
                print(f"errors: {df_qc.loc[failed_row, column+'.error'].values}")
                print("\n")
        except:
            pass
    
    