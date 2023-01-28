from subject_loader import SubjectLoader


# 1) Calling class instance with directory:

loader = SubjectLoader("/home/hpcmcco1/trial_data/pilot_dataset/MELD_H101")

# 2) Providing a subject id using helper:

print(loader.cohort_ids())

example_id = loader.cohort_ids()[0]

loader.subject_id = example_id

print(f'Chosen subject id: {example_id}')

# 3) Providing an imaging modality using helper:

example_mod = loader.list_possible_mods()[0]
loader.modality = example_mod

print(f'Chosen imaging modality: {example_mod}')


# 4) CSV Methods:

print(loader.cohort_data())

print(loader.demographic_features())

print(loader.present_demographic_features())

print(f"Age at surgery: {loader.extract_demographic_variable('age_at_surgery')}")


# 5) Json Methods:

print(loader.output_json())

print(loader.list_json_vars())

print(f'ImagingFrequency: {loader.extract_json_var("ImagingFrequency")}')


# 6) Saving Visualisation: 

loader.display_image_seg(display_seg=False, save_name='no_segment')
loader.display_image_seg(display_seg=True, superimpose=False,save_name='yes_segment')
loader.display_image_seg(display_seg=True, superimpose=True,save_name='super_segment')




