from parameters import Config
from registration import Registration
import os
import shutil
import SimpleITK as sitk
import json
import pandas as pd
from displaymod import DisplayModalities
import markdown
import re
import time
import numpy as np
from synthseg_registration import SynthSegRegistration


class DirectoryRegistration:

    def __init__(self):

        config = Config()

        self.orig_bids_folder = config.orig_bids_folder  # './MELD_H101/'
        self.list_subjects = config.list_subjects
        self.save_dir = config.save_dir  # './Task704_MELDH4/'

        self.mask_in_flair = config.mask_in_flair

        self.t1_tail = config.t1_tail
        self.flair_tail = config.flair_tail
        self.t2_tail = config.t2_tail
        self.t1_postop_tail = config.t1_postop_tail

        self.mask_tail = config.mask_tail

        self.preop_dwi_tail = config.preop_dwi_tail
        self.preop_DWInegPE_tail = config.preop_DWInegPE_tail

        self.use_synthseg = config.use_synthseg

        self.registration_helper = SynthSegRegistration() if self.use_synthseg else Registration()

        self.display_helper = DisplayModalities()

        self.image_save_dir = config.img_save_dir

        self.create_dir(self.save_dir)
        self.create_dir(self.image_save_dir)

        self.t1_pth = None
        self.flair_pth = None
        self.t2_pth = None
        self.t1_postop_pth = None
        self.mask_pth = None
        self.preop_dwi_pth = None
        self.preop_DWInegPE_pth = None

        self.flair_reg = None
        self.t2_reg = None
        self.t1_postop_reg = None
        self.mask_reg = None
        self.preop_dwi_reg = None
        self.preop_DWInegPE_reg = None

        self.matrix_save_name = config.matrix_save_name
        self.data_matrix = self.init_dataframe()

        markdown_file = config.markdown_file
        html_file = config.html_file

        self.markdown_pth = os.path.join(self.image_save_dir, markdown_file)
        self.html_pth = os.path.join(self.image_save_dir, html_file)
        self.markdown_title = config.markdown_title
        self.initialize_markdown()

        self.synth_save_dir = config.synth_save_dir
        self.create_dir(self.synth_save_dir) if self.synth_save_dir is not None else None

        # dice_scores, dice_average, dice_stdev
        self.flair_dice = None
        self.t2_dice = None
        self.t1_postop_dice = None
        self.mask_dice = None
        self.preop_dwi_dice = None
        self.preop_DWInegPE_dice = None

    @staticmethod
    def create_dir(dir):
        if not os.path.exists(dir):
            os.mkdir(dir)

    def init_dataframe(self):

        if not os.path.exists(os.path.join(self.save_dir, self.matrix_save_name)):
            columns = ["Subject", "T1-Preop Present", "T1-Preop Correct Mod.", "T1-Preop Artefact", "T1-Preop FOV" ,"T1-Preop Defacing",
                        "FLAIR Present", "FLAIR Register", "FLAIR Correct Mod.", "FLAIR Artefact", "FLAIR FOV", "FLAIR Defacing",
                        "T2 Present", "T2 Register", "T2 Correct Mod.", "T2 Artefact", "T2 FOV", "T2 Defacing",
                        "T1-Postop Present", "T1-Postop Register", "T1-Postop Correct Mod.", "T1-Postop Artefact","T1-Postop FOV", 
                        "T1-Postop Defacing", "DWI-Preop Present", "DWI-Preop Register", "DWI-Preop Correct Mod.",
                        "DWI-Preop Artefact", "DWI-Preop FOV", "DWI-Preop Defacing", "DWInegPE-Preop Present", "DWInegPE-Preop Register",
                        "DWInegPE-Preop Correct Mod.", "DWInegPE-Preop Artefact","DWInegPE-Preop FOV", "DWInegPE-Preop Defacing",
                        "Mask Present", "Mask QC"]
            descriptions_dict = {"Subject" : np.nan,
                    "Present" : "1-yes, 0-no",
                    "Register" : "1-yes, 0-no",
                    "Correct Mod." : "1-yes, 2-no wrong sequence, 3-Contrast, 4-possible previous resection, 5-unable to see resection",
                    "Artefact" : "1-no artefact seen, 2-small artefact, 3-large artefact",
                    "FOV" : "1- entire brain 2- cropped",
                    "Defacing" : "1-good defacing, 2-face remaining, 3-small amount of brain removed, 4-large amount of brain removed",
                    "Mask QC" : "1-good and same location as resection, 2-good (no post-op available), 3-looks wrong location and needs further investigation, 4-problem with file, 5-not available"                     
                    }
            descriptions=[]
            for column in columns:
                for key in descriptions_dict:
                    if key in column: 
                        descriptions.append(descriptions_dict[key])
            df = pd.DataFrame(np.array([descriptions]), columns=columns)
        else:
            df = pd.read_csv(os.path.join(self.save_dir, self.matrix_save_name))

        return df

    def file_names_init(self):

        self.t1_pth = None
        self.flair_pth = None
        self.t2_pth = None
        self.t1_postop_pth = None
        self.mask_pth = None
        self.preop_dwi_pth = None
        self.preop_DWInegPE_pth = None

        self.flair_reg = None
        self.t2_reg = None
        self.t1_postop_reg = None
        self.mask_reg = None
        self.preop_dwi_reg = None
        self.preop_DWInegPE_reg = None

        self.flair_dice = None
        self.t2_dice = None
        self.t1_postop_dice = None
        self.mask_dice = None
        self.preop_dwi_dice = None
        self.preop_DWInegPE_dice = None

    def directory_cases(self):
        if self.list_subjects!=None:
            print(["sub-"+ ''.join(name.split('_')) for name in pd.read_csv(self.list_subjects)['id'].values])
            return ["sub-"+ ''.join(name.split('_')) for name in pd.read_csv(self.list_subjects)['id'].values]
        else:
            print([name for name in os.listdir(self.orig_bids_folder) if "sub" in name])
            return [name for name in os.listdir(self.orig_bids_folder) if "sub" in name]  # this is a list names.

    def modality_check(self, case):
        # return list of avaible modality paths + print out which modalities are and aren't avaible for case

        anat_folder_pth = os.path.join(self.orig_bids_folder, case, "anat")
        dwi_folder_pth = os.path.join(self.orig_bids_folder, case, "dwi")

        self.file_names_init()

        if os.path.exists(anat_folder_pth):  # make robust to capitalisation
            for filename in os.listdir(anat_folder_pth):
                if filename.lower().endswith(self.t1_tail.lower()):
                    self.t1_pth = filename
                elif filename.lower().endswith(self.flair_tail.lower()):
                    self.flair_pth = filename
                elif filename.lower().endswith(self.t2_tail.lower()):
                    self.t2_pth = filename
                elif filename.lower().endswith(self.t1_postop_tail.lower()):
                    self.t1_postop_pth = filename
                elif filename.lower().endswith(self.mask_tail.lower()):
                    self.mask_pth = filename

        if os.path.exists(dwi_folder_pth):
            for filename in os.listdir(dwi_folder_pth):
                if filename.lower().endswith(self.preop_dwi_tail.lower()):
                    self.preop_dwi_pth = filename
                elif filename.lower().endswith(self.preop_DWInegPE_tail.lower()):
                    self.preop_DWInegPE_pth = filename

    def three_dim_check(self, pth_1):

        img_1 = sitk.ReadImage(pth_1)
        return img_1.GetDimension() == 3

    def register(self, fixed_img_pth, moving_img_pth, save_moving_img_pth):

        self.registration_helper.set_fixed_img(fixed_img_pth)
        self.registration_helper.registation_trx(moving_img_pth)
        self.registration_helper.transform(moving_img_pth, save_moving_img_pth)

    def synthseg_register(self, fixed_img_pth, moving_img_pth, save_moving_img_pth, synth_save_dir,
                          fwd_field_pth, is_postop=False):

        return self.registration_helper.register(fixed_img_pth, moving_img_pth,
                                                 save_moving_img_pth, synth_save_dir,
                                                 fwd_field_pth, is_postop)

    def register_label(self, fixed_img_pth, moving_img_pth, moving_label_pth, save_moving_label_pth):

        self.registration_helper.set_fixed_img(fixed_img_pth)
        self.registration_helper.registation_trx(moving_img_pth)
        self.registration_helper.transform(moving_label_pth, save_moving_label_pth, label=True)

    def json_edit(self, json_old_pth, json_new_pth, value, key="SpatialReference"):
        """Add a key-value pair to a JSON file."""

        # Check if the file exists before trying to read
        try:
            with open(json_old_pth, 'r') as file:
                data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {}  # if file does not exist or is empty/invalid, initialize data as an empty dictionary

        # Add the new key-value pair to the dictionary
        data[key] = value

        # Write the updated dictionary back to the JSON file
        with open(json_new_pth, 'w') as file:
            json.dump(data, file, indent=4)

    def matrix_update(self, case):

        new_data = pd.DataFrame({"Subject": [case], "T1-Preop Present": [1 if self.t1_pth is not None else 0],
                                 "T1-Preop Correct Mod.": None,
                                 "T1-Preop Artefact": None, "T1-Preop FOV": None, "T1-Preop Defacing": None,
                                 "FLAIR Present": [1 if self.flair_pth is not None else 0],
                                 "FLAIR Register": [1 if self.flair_reg is not None else 0],
                                 "FLAIR Correct Mod.": None,
                                 "FLAIR Artefact": None, "FLAIR FOV": None, "FLAIR Defacing": None,
                                 "T2 Present": [1 if self.t2_pth is not None else 0],
                                 "T2 Register": [1 if self.t2_reg is not None else 0],
                                 "T2 Correct Mod.": None,
                                 "T2 Artefact": None, "T2 FOV": None, "T2 Defacing": None,
                                 "T1-Postop Present": [1 if self.t1_postop_pth is not None else 0],
                                 "T1-Postop Register": [1 if self.t1_postop_reg is not None else 0],
                                 "T1-Postop Correct Mod.": None,
                                 "T1-Postop Artefact": None, "T1-Postop FOV": None,  "T1-Postop Defacing": None,
                                 "DWI-Preop Present": [1 if self.preop_dwi_pth is not None else 0],
                                 "DWI-Preop Register": [1 if self.preop_dwi_reg is not None else 0],
                                 "DWI-Preop Correct Mod.": None,
                                 "DWI-Preop Artefact": None, "DWI-Preop FOV": None, "DWI-Preop Defacing": None,
                                 "DWInegPE-Preop Present": [1 if self.preop_DWInegPE_pth is not None else 0],
                                 "DWInegPE-Preop Register": [1 if self.preop_DWInegPE_reg is not None else 0],
                                 "DWInegPE-Preop Correct Mod.": None,
                                 "DWInegPE-Preop Artefact": None, "DWInegPE-Preop FOV": None,  "DWInegPE-Preop Defacing": None,
                                 "Mask Present": [1 if self.mask_pth is not None else 0], "Mask QC": None})

        self.data_matrix = pd.concat([self.data_matrix, new_data], ignore_index=True)

    def case_registration(self, case):

        # register everything to t1
        self.file_names_init()
        self.modality_check(case)

        print("I'm here")
        anat_folder_pth = os.path.join(self.orig_bids_folder, case, "anat")
        dwi_folder_pth = os.path.join(self.orig_bids_folder, case, "dwi")

        save_anat_folder_pth = os.path.join(self.save_dir, case, "anat")
        save_dwi_folder_pth = os.path.join(self.save_dir, case, "dwi")

        # if not os.path.exists(save_anat_folder_pth):  # only do this for not previously done cases

        if os.path.exists(anat_folder_pth):
            self.create_dir(os.path.join(self.save_dir, case))  # create case folder
            self.create_dir(save_anat_folder_pth)  # create anat folder

        if os.path.exists(dwi_folder_pth):
            self.create_dir(os.path.join(self.save_dir, case))  # create case folder
            self.create_dir(save_dwi_folder_pth)  # create anat folder

        fixed_img_pth = os.path.join(anat_folder_pth, self.t1_pth)

        shutil.copy(fixed_img_pth, os.path.join(save_anat_folder_pth, self.t1_pth))

        if not self.three_dim_check(fixed_img_pth):
            raise Exception(f"T1 is not 3D for case: {case}")
        shutil.copy(os.path.join(anat_folder_pth, self.t1_pth.replace(".nii.gz", ".json")),
                    os.path.join(save_anat_folder_pth, self.t1_pth.replace(".nii.gz", ".json")))

        self.qc_imgs(case, fixed_img_pth, "T1")

        # copy over orig label if mask not in flair modality
        if not self.mask_in_flair:
            if self.mask_pth is not None:
                if os.path.exists(os.path.join(anat_folder_pth, self.mask_pth)):

                    if self.three_dim_check(os.path.join(anat_folder_pth, self.mask_pth)):
                        shutil.copy(os.path.join(anat_folder_pth, self.mask_pth), os.path.join(save_anat_folder_pth, self.mask_pth))

                        shutil.copy(os.path.join(anat_folder_pth, self.mask_pth.replace(".nii.gz", ".json")),
                                    os.path.join(save_anat_folder_pth, self.mask_pth.replace(".nii.gz", ".json")))
                        self.mask_reg = 1
                    else:
                        print(f"Warning: Mask is not 3D for case: {case}")

            # flair
            if self.flair_pth is not None:
                moving_img_pth = os.path.join(anat_folder_pth, self.flair_pth)

                if self.three_dim_check(moving_img_pth):
                    save_moving_img_pth = os.path.join(save_anat_folder_pth, self.flair_pth.replace(".nii.gz", "_space-T1.nii.gz"))
                    # if not os.path.isfile(save_moving_img_pth):
                    print('register flair')
                    self.register(fixed_img_pth, moving_img_pth, save_moving_img_pth)
                    # else:
                    #     print('flair already registered')
                    self.json_edit(json_old_pth=os.path.join(anat_folder_pth, self.flair_pth.replace(".nii.gz", ".json")),
                                   json_new_pth=os.path.join(save_anat_folder_pth, self.flair_pth.replace(".nii.gz", ".json")),
                                   value=fixed_img_pth)  # edit json
                    self.qc_imgs(case, save_moving_img_pth, "FLAIR")
                    self.flair_reg = 1

                    if self.mask_in_flair:
                        moving_label_pth = os.path.join(anat_folder_pth, self.mask_pth)
                        save_moving_label_pth = os.path.join(save_anat_folder_pth, self.mask_pth.replace(".nii.gz", "_space-T1.nii.gz"))
                        self.register_label(fixed_img_pth, moving_img_pth, moving_label_pth, save_moving_label_pth)

                        self.json_edit(json_old_pth=os.path.join(anat_folder_pth, self.mask_pth.replace(".nii.gz", ".json")),
                                       json_new_pth=os.path.join(save_anat_folder_pth, self.mask_pth.replace(".nii.gz", ".json")),
                                       value=fixed_img_pth)  # edit json
                        self.mask_reg = 1
                else:
                    print(f"Warning: Flair is not 3D for case: {case}")

            # T2
            if self.t2_pth is not None:
                moving_img_pth = os.path.join(anat_folder_pth, self.t2_pth)
                if self.three_dim_check(moving_img_pth):

                    save_moving_img_pth = os.path.join(save_anat_folder_pth, self.t2_pth.replace(".nii.gz", "_space-T1.nii.gz"))
                    # if not os.path.isfile(save_moving_img_pth):
                    print('register T2')
                    self.register(fixed_img_pth, moving_img_pth, save_moving_img_pth)
                    # else:
                    #     print('T2 already registered')
                    self.json_edit(json_old_pth=os.path.join(anat_folder_pth, self.t2_pth.replace(".nii.gz", ".json")),
                                   json_new_pth=os.path.join(save_anat_folder_pth, self.t2_pth.replace(".nii.gz", ".json")),
                                   value=fixed_img_pth)  # edit json
                    self.qc_imgs(case, save_moving_img_pth, "T2")
                    self.t2_reg = 1

                else:
                    print(f"Warning: T2 is not 3D for case: {case}")


            # T1 post-op
            if self.t1_postop_pth is not None:
                moving_img_pth = os.path.join(anat_folder_pth, self.t1_postop_pth)
                if self.three_dim_check(moving_img_pth):

                    save_moving_img_pth = os.path.join(save_anat_folder_pth, self.t1_postop_pth.replace(".nii.gz", "_space-T1.nii.gz"))
                    # if not os.path.isfile(save_moving_img_pth):
                    print('register post-op')
                    self.register(fixed_img_pth, moving_img_pth, save_moving_img_pth)
                    # else:
                    #     print('post-op already registered')
                    self.json_edit(json_old_pth=os.path.join(anat_folder_pth, self.t1_postop_pth.replace(".nii.gz", ".json")),
                                   json_new_pth=os.path.join(save_anat_folder_pth, self.t1_postop_pth.replace(".nii.gz", ".json")),
                                   value=fixed_img_pth)  # edit json
                    self.qc_imgs(case, save_moving_img_pth, "T1-postop")
                    self.t1_postop_reg = 1

                else:
                    print(f"Warning: T1-postop is not 3D for case: {case}")

            # preop_dwi
            if self.preop_dwi_pth is not None:
                moving_img_pth = os.path.join(dwi_folder_pth, self.preop_dwi_pth)
                if self.three_dim_check(moving_img_pth):

                    save_moving_img_pth = os.path.join(save_dwi_folder_pth, self.preop_dwi_pth.replace(".nii.gz", "_space-T1.nii.gz"))
                    # if not os.path.isfile(save_moving_img_pth):
                    print('register dwi')
                    self.register(fixed_img_pth, moving_img_pth, save_moving_img_pth)
                    # else:
                    #     print('dwi already registered')
                    self.json_edit(json_old_pth=os.path.join(dwi_folder_pth, self.preop_dwi_pth.replace(".nii.gz", ".json")),
                                   json_new_pth=os.path.join(save_dwi_folder_pth, self.preop_dwi_pth.replace(".nii.gz", ".json")),
                                   value=fixed_img_pth)  # edit json
                    self.qc_imgs(case, save_moving_img_pth, "preop_dwi")
                    self.preop_dwi_reg = 1
                else:
                    print(f"Warning: preop_dwi is not 3D for case: {case}")

            # preop_dwi
            if self.preop_DWInegPE_pth is not None:
                moving_img_pth = os.path.join(dwi_folder_pth, self.preop_DWInegPE_pth)
                if self.three_dim_check(moving_img_pth):

                    save_moving_img_pth = os.path.join(save_dwi_folder_pth, self.preop_DWInegPE_pth.replace(".nii.gz", "_space-T1.nii.gz"))
                    # if not os.path.isfile(save_moving_img_pth):
                    print('register dwinegPE')
                    self.register(fixed_img_pth, moving_img_pth, save_moving_img_pth)
                    # else:
                    #     print('dwinegPE already registered')
                    self.json_edit(json_old_pth=os.path.join(dwi_folder_pth, self.preop_DWInegPE_pth.replace(".nii.gz", ".json")),
                                   json_new_pth=os.path.join(save_dwi_folder_pth, self.preop_DWInegPE_pth.replace(".nii.gz", ".json")),
                                   value=fixed_img_pth)  # edit json
                    self.qc_imgs(case, save_moving_img_pth, "preop_DWInegPE")
                    self.preop_DWInegPE_reg = 1
                else:
                    print(f"Warning: preop_DWInegPE is not 3D for case: {case}")

            self.matrix_update(case)

            # overlay qc: #### add option if seg is none
            if self.mask_pth is not None:
                if self.mask_in_flair:
                    self.overlay_qc(case=case,
                                    t1=os.path.join(save_anat_folder_pth, self.t1_pth),
                                    post_op=os.path.join(save_anat_folder_pth, self.t1_postop_pth.replace(".nii.gz", "_space-T1.nii.gz")
                                                         ) if self.t1_postop_pth is not None else None,
                                    seg=os.path.join(save_anat_folder_pth, self.mask_pth.replace(".nii.gz", "_space-T1.nii.gz")))
                else:
                    self.overlay_qc(case=case,
                                    t1=os.path.join(save_anat_folder_pth, self.t1_pth),
                                    post_op=os.path.join(save_anat_folder_pth, self.t1_postop_pth.replace(".nii.gz", "_space-T1.nii.gz")
                                                         ) if self.t1_postop_pth is not None else None,
                                    seg=os.path.join(save_anat_folder_pth, self.mask_pth))
            else:
                print(f"Mask QC not possible as mask not provided for case: {case}")

            self.add_case_to_markdown(case)

    def synthseg_case_registration(self, case):
        
        output = True
        
        # register everything to t1
        self.file_names_init()
        self.modality_check(case)

        anat_folder_pth = os.path.join(self.orig_bids_folder, case, "anat")
        dwi_folder_pth = os.path.join(self.orig_bids_folder, case, "dwi")

        save_anat_folder_pth = os.path.join(self.save_dir, case, "anat")
        save_dwi_folder_pth = os.path.join(self.save_dir, case, "dwi")

        save_synth_anat_folder_pth = os.path.join(self.synth_save_dir, case, "anat")
        save_synth_dwi_folder_pth = os.path.join(self.synth_save_dir, case, "dwi")

        # if not os.path.exists(save_anat_folder_pth):  # only do this for not previously done cases

        if os.path.exists(anat_folder_pth):
            self.create_dir(os.path.join(self.save_dir, case))  # create case folder
            self.create_dir(save_anat_folder_pth)  # create anat folder

            self.create_dir(os.path.join(self.synth_save_dir, case))  # create case folder
            self.create_dir(save_synth_anat_folder_pth)  # create anat folder

        if os.path.exists(dwi_folder_pth):
            self.create_dir(os.path.join(self.save_dir, case))  # create case folder
            self.create_dir(save_dwi_folder_pth)  # create anat folder

            self.create_dir(os.path.join(self.synth_save_dir, case))  # create case folder
            self.create_dir(save_synth_dwi_folder_pth)  # create anat folder
        
        try: 
            fixed_img_pth = os.path.join(anat_folder_pth, self.t1_pth)
            if os.path.isfile(fixed_img_pth):
                shutil.copy(fixed_img_pth, os.path.join(save_anat_folder_pth, self.t1_pth))
        except:
                print(f'COPY T1 FAILED with error')
                return False
            
        
        if not self.three_dim_check(fixed_img_pth):
            raise Exception(f"T1 is not 3D for case: {case}")
        if not os.path.isfile(os.path.join(save_anat_folder_pth, self.t1_pth.replace(".nii.gz", ".json"))):
            shutil.copy(os.path.join(anat_folder_pth, self.t1_pth.replace(".nii.gz", ".json")),
                    os.path.join(save_anat_folder_pth, self.t1_pth.replace(".nii.gz", ".json")))

        self.qc_imgs(case, fixed_img_pth, "T1")

        # copy over orig label if mask not in flair modality
        if not self.mask_in_flair:
            if self.mask_pth is not None:
                if os.path.exists(os.path.join(anat_folder_pth, self.mask_pth)):

                    if self.three_dim_check(os.path.join(anat_folder_pth, self.mask_pth)):
                        shutil.copy(os.path.join(anat_folder_pth, self.mask_pth), os.path.join(save_anat_folder_pth, self.mask_pth))

                        shutil.copy(os.path.join(anat_folder_pth, self.mask_pth.replace(".nii.gz", ".json")),
                                    os.path.join(save_anat_folder_pth, self.mask_pth.replace(".nii.gz", ".json")))
                        self.mask_reg = 1
                    else:
                        print(f"Warning: Mask is not 3D for case: {case}")

        # flair
        if self.flair_pth is not None:
            moving_img_pth = os.path.join(anat_folder_pth, self.flair_pth)

            if self.three_dim_check(moving_img_pth):
                save_moving_img_pth = os.path.join(save_anat_folder_pth, self.flair_pth.replace(".nii.gz", "_space-T1.nii.gz"))
                # if not os.path.isfile(save_moving_img_pth):
                print('register FLAIR')
                fwd_field_pth = os.path.join(save_synth_anat_folder_pth, "FLAIR_fwdfield.nii.gz")
                self.flair_dice = self.synthseg_register(fixed_img_pth=fixed_img_pth, moving_img_pth=moving_img_pth,
                                                        save_moving_img_pth=save_moving_img_pth,
                                                        synth_save_dir=save_synth_anat_folder_pth,
                                                        fwd_field_pth=fwd_field_pth, is_postop=False)
                if not self.flair_dice:
                    print(f'ERROR: Process failed for FLAIR for subject {case}')
                    output = False
                else:
                # else:
                #     print('FLAIR already registered')
                    self.json_edit(json_old_pth=os.path.join(anat_folder_pth, self.flair_pth.replace(".nii.gz", ".json")),
                                    json_new_pth=os.path.join(save_anat_folder_pth, self.flair_pth.replace(".nii.gz", ".json")),
                                    value=fixed_img_pth)  # edit json
                    self.qc_imgs(case, save_moving_img_pth, "FLAIR")
                    self.flair_reg = 1

                    if self.mask_in_flair:
                        moving_label_pth = os.path.join(anat_folder_pth, self.mask_pth)
                        save_moving_label_pth = os.path.join(save_anat_folder_pth, self.mask_pth.replace(".nii.gz", "_space-T1.nii.gz"))
                        # if not os.path.isfile(save_moving_label_pth):
                        print('register lesion mask FLAIR')
                        self.register_label(fixed_img_pth, moving_img_pth, moving_label_pth, save_moving_label_pth)
                        # else:
                        #     print('lesion mask FLAIR already registered')
                        self.json_edit(json_old_pth=os.path.join(anat_folder_pth, self.mask_pth.replace(".nii.gz", ".json")),
                                        json_new_pth=os.path.join(save_anat_folder_pth, self.mask_pth.replace(".nii.gz", ".json")),
                                        value=fixed_img_pth)  # edit json
                        self.mask_reg = 1
            else:
                print(f"Warning: Flair is not 3D for case: {case}")

        # T2
        if self.t2_pth is not None:
            moving_img_pth = os.path.join(anat_folder_pth, self.t2_pth)

            if self.three_dim_check(moving_img_pth):

                save_moving_img_pth = os.path.join(save_anat_folder_pth, self.t2_pth.replace(".nii.gz", "_space-T1.nii.gz"))
                # if not os.path.isfile(save_moving_img_pth):
                print('register T2')
                fwd_field_pth = os.path.join(save_synth_anat_folder_pth, "T2_fwdfield.nii.gz")
                self.t2_dice = self.synthseg_register(fixed_img_pth=fixed_img_pth, moving_img_pth=moving_img_pth,
                                                            save_moving_img_pth=save_moving_img_pth,
                                                            synth_save_dir=save_synth_anat_folder_pth,
                                                            fwd_field_pth=fwd_field_pth, is_postop=False)
                if not self.t2_dice:
                    print(f'ERROR: Process failed for T2 for subject {case}')
                    output = False
                else:
                # else:
                #     print('T2 already registered')
                    self.json_edit(json_old_pth=os.path.join(anat_folder_pth, self.t2_pth.replace(".nii.gz", ".json")),
                                    json_new_pth=os.path.join(save_anat_folder_pth, self.t2_pth.replace(".nii.gz", ".json")),
                                    value=fixed_img_pth)  # edit json
                    self.qc_imgs(case, save_moving_img_pth, "T2")
                    self.t2_reg = 1

            else:
                print(f"Warning: T2 is not 3D for case: {case}")

        # T1 post-op
        if self.t1_postop_pth is not None:
            moving_img_pth = os.path.join(anat_folder_pth, self.t1_postop_pth)

            if self.three_dim_check(moving_img_pth):

                save_moving_img_pth = os.path.join(save_anat_folder_pth, self.t1_postop_pth.replace(".nii.gz", "_space-T1.nii.gz"))
                # if not os.path.isfile(save_moving_img_pth):
                print('register T1 post-op')
                fwd_field_pth = os.path.join(save_synth_anat_folder_pth, "T1postop_fwdfield.nii.gz")
                self.t1_postop_dice = self.synthseg_register(fixed_img_pth=fixed_img_pth, moving_img_pth=moving_img_pth,
                                                            save_moving_img_pth=save_moving_img_pth,
                                                            synth_save_dir=save_synth_anat_folder_pth,
                                                            fwd_field_pth=fwd_field_pth, is_postop=True)
                if not self.t1_postop_dice:
                    print(f'ERROR: Process failed for T1-postop for subject {case}')
                    output = False
                # else:
                #     print('T1 post-op already registered')
                else:
                    self.json_edit(json_old_pth=os.path.join(anat_folder_pth, self.t1_postop_pth.replace(".nii.gz", ".json")),
                                    json_new_pth=os.path.join(save_anat_folder_pth, self.t1_postop_pth.replace(".nii.gz", ".json")),
                                    value=fixed_img_pth)  # edit json
                    self.qc_imgs(case, save_moving_img_pth, "T1-postop")
                    self.t1_postop_reg = 1

            else:
                print(f"Warning: T1-postop is not 3D for case: {case}")

        # preop_dwi
        if self.preop_dwi_pth is not None:
            moving_img_pth = os.path.join(dwi_folder_pth, self.preop_dwi_pth)
            if self.three_dim_check(moving_img_pth):

                save_moving_img_pth = os.path.join(save_dwi_folder_pth, self.preop_dwi_pth.replace(".nii.gz", "_space-T1.nii.gz"))
                # if not os.path.isfile(save_moving_img_pth):
                print('register DWI')
                fwd_field_pth = os.path.join(save_synth_dwi_folder_pth, "preop_dwi_fwdfield.nii.gz")
                self.preop_dwi_dice = self.synthseg_register(fixed_img_pth=fixed_img_pth, moving_img_pth=moving_img_pth,
                                                            save_moving_img_pth=save_moving_img_pth,
                                                            synth_save_dir=save_synth_dwi_folder_pth,
                                                            fwd_field_pth=fwd_field_pth, is_postop=False)
                if not self.preop_dwi_dice:
                    print(f'ERROR: Process failed for DWI-preop for subject {case}')
                    output = False
                # else:
                #     print('DWI already registered')
                else:
                    self.json_edit(json_old_pth=os.path.join(dwi_folder_pth, self.preop_dwi_pth.replace(".nii.gz", ".json")),
                                    json_new_pth=os.path.join(save_dwi_folder_pth, self.preop_dwi_pth.replace(".nii.gz", ".json")),
                                    value=fixed_img_pth)  # edit json
                    self.qc_imgs(case, save_moving_img_pth, "preop_dwi")
                    self.preop_dwi_reg = 1
            else:
                print(f"Warning: preop_dwi is not 3D for case: {case}")

        # preop_DWInegPE
        if self.preop_DWInegPE_pth is not None:
            moving_img_pth = os.path.join(dwi_folder_pth, self.preop_DWInegPE_pth)
            if self.three_dim_check(moving_img_pth):

                save_moving_img_pth = os.path.join(save_dwi_folder_pth, self.preop_DWInegPE_pth.replace(".nii.gz", "_space-T1.nii.gz"))
                # if not os.path.isfile(save_moving_img_pth):
                print('register DWInegPE')
                fwd_field_pth = os.path.join(save_synth_dwi_folder_pth, "preop_DWInegPE_fwdfield.nii.gz")
                self.preop_DWInegPE_dice = self.synthseg_register(fixed_img_pth=fixed_img_pth, moving_img_pth=moving_img_pth,
                                                                save_moving_img_pth=save_moving_img_pth,
                                                                synth_save_dir=save_synth_dwi_folder_pth,
                                                                fwd_field_pth=fwd_field_pth, is_postop=False)
                if not self.preop_DWInegPE_dice:
                    print(f'ERROR: Process failed for DWInegPE-preop for subject {case}')
                    output = False
                # else:
                #     print('DWInegPE already registered')
                else:
                    self.json_edit(json_old_pth=os.path.join(dwi_folder_pth, self.preop_DWInegPE_pth.replace(".nii.gz", ".json")),
                                    json_new_pth=os.path.join(save_dwi_folder_pth, self.preop_DWInegPE_pth.replace(".nii.gz", ".json")),
                                    value=fixed_img_pth)  # edit json
                    self.qc_imgs(case, save_moving_img_pth, "preop_DWInegPE")
                    self.preop_DWInegPE_reg = 1
            else:
                print(f"Warning: preop_DWInegPE is not 3D for case: {case}")

        if output == False:
            return False
        
        self.matrix_update(case)

        # overlay qc: #### add option if seg is none
        if self.mask_pth is not None:
            if self.mask_in_flair:
                self.overlay_qc(case=case,
                                t1=os.path.join(save_anat_folder_pth, self.t1_pth),
                                post_op=os.path.join(save_anat_folder_pth, self.t1_postop_pth.replace(".nii.gz", "_space-T1.nii.gz")
                                                        ) if self.t1_postop_pth is not None else None,
                                seg=os.path.join(save_anat_folder_pth, self.mask_pth.replace(".nii.gz", "_space-T1.nii.gz")))
            else:
                self.overlay_qc(case=case,
                                t1=os.path.join(save_anat_folder_pth, self.t1_pth),
                                post_op=os.path.join(save_anat_folder_pth, self.t1_postop_pth.replace(".nii.gz", "_space-T1.nii.gz")
                                                        ) if self.t1_postop_pth is not None else None,
                                seg=os.path.join(save_anat_folder_pth, self.mask_pth))
        else:
            print(f"Mask QC not possible as mask not provided for case: {case}")

        self.add_case_to_markdown(case)

        return True
    
    def directory_registration(self):

        bids_cases = self.directory_cases()

        for bids_case in bids_cases:
            start_time = time.time()
            print(f"Registration starting for case: {bids_case}")
            output = self.case_registration(bids_case) if not self.use_synthseg else self.synthseg_case_registration(bids_case)
            if not output :
                print(f"Registration failed for case: {bids_case}")
            else:
                print(f"Registration complete for case: {bids_case}")
            end_time = time.time()
            print(f"Time Elapsed: {end_time-start_time:.2f}\n")

        self.convert_md_to_html()
        self.data_matrix.to_csv(os.path.join(self.save_dir, self.matrix_save_name), index=False)

    def qc_imgs(self, case, img, modality):

        case_img_pth = os.path.join(self.image_save_dir, case)
        self.create_dir(case_img_pth)
        save_img_sag_cor = os.path.join(case_img_pth, f"{case}_{modality}_sagittal_coronal.png")
        self.display_helper.display_image_sag_coron(img, save_name=save_img_sag_cor)

    def overlay_qc(self, case, t1, post_op, seg):

        case_img_pth = os.path.join(self.image_save_dir, case)
        save_img_sag_cor = os.path.join(case_img_pth, f"{case}_segment_overlay_sagital_coronal.png")
        self.display_helper.display_overlay_sag_coron(t1=t1, post_op=post_op, seg=seg, save_name=save_img_sag_cor)

    def initialize_markdown(self):

        if not os.path.exists(self.markdown_pth):
            with open(self.markdown_pth, 'w') as md_file:
                md_file.write(f"## {self.markdown_title}\n\n")

    def add_dice_scores_to_markdown(self, dice_scores, avg_dice, dice_std):

        dice_scores_str_outlier = ', '.join(str(score) for score in dice_scores if score<0.7)
        print(dice_scores_str_outlier)
        with open(self.markdown_pth, 'a') as md_file:
            md_file.write(f"**Avg Dice (stdev): {avg_dice} ({dice_std})**\n\n")
            md_file.write(f"**Dice Scores below 0.7: {dice_scores_str_outlier}**\n\n")

    def add_image_to_markdown(self, image_path, description):

        with open(self.markdown_pth, 'a') as md_file:
            md_file.write(f"##### {description}\n\n")
            md_file.write(f'![{description}]({image_path})\n\n')

    def add_saggital_coronal_markdown(self, case_img_pth, case, modality):
        save_img_sag_cor = os.path.join(case_img_pth, f"{case}_{modality}_sagittal_coronal.png")
        self.add_image_to_markdown(save_img_sag_cor, f"{modality} Sagittal & Coronal")
        
    def add_saggital_markdown(self, case_img_pth, case, modality):
        save_img_sag = os.path.join(case_img_pth, f"{case}_{modality}_sagittal.png")
        self.add_image_to_markdown(save_img_sag, f"{modality} Sagittal")

    def add_coronal_markdown(self, case_img_pth, case, modality):
        save_img_coron = os.path.join(case_img_pth, f"{case}_{modality}_coronal.png")
        self.add_image_to_markdown(save_img_coron, f"{modality} Coronal")

    def add_case_to_markdown(self, case):

        with open(self.markdown_pth, 'a') as md_file:
            md_file.write('---\n\n')  # Horizontal rule
            md_file.write(f'### Case: {case}\n\n')  # New title

        case_img_pth = os.path.join("./", case)  # os.path.join(self.image_save_dir, case)

        # adding sagittal & coronal on same row
        self.add_saggital_coronal_markdown(case_img_pth, case, modality="T1") if self.t1_pth is not None else None
        self.add_saggital_coronal_markdown(case_img_pth, case, modality="FLAIR") if self.flair_reg is not None else None
        self.add_dice_scores_to_markdown(self.flair_dice[0], self.flair_dice[1], self.flair_dice[2]) if self.flair_dice is not None else None
        self.add_saggital_coronal_markdown(case_img_pth, case, modality="T2") if self.t2_reg is not None else None
        self.add_dice_scores_to_markdown(self.t2_dice[0], self.t2_dice[1], self.t2_dice[2]) if self.t2_dice is not None else None
        self.add_saggital_coronal_markdown(case_img_pth, case, modality="T1-postop") if self.t1_postop_reg is not None else None
        self.add_dice_scores_to_markdown(self.t1_postop_dice[0], self.t1_postop_dice[1], self.t1_postop_dice[2]) if self.t1_postop_dice is not None else None
        self.add_saggital_coronal_markdown(case_img_pth, case, modality="preop_dwi") if self.preop_dwi_reg is not None else None
        self.add_dice_scores_to_markdown(self.preop_dwi_dice[0], self.preop_dwi_dice[1], self.preop_dwi_dice[2]) if self.preop_dwi_dice is not None else None
        self.add_saggital_coronal_markdown(case_img_pth, case, modality="preop_DWInegPE") if self.preop_DWInegPE_reg is not None else None
        self.add_dice_scores_to_markdown(self.preop_DWInegPE_dice[0], self.preop_DWInegPE_dice[1], self.preop_DWInegPE_dice[2]) if self.preop_DWInegPE_dice is not None else None


        if self.mask_reg is not None:
            save_img_sag_cor = os.path.join(case_img_pth, f"{case}_segment_overlay_sagital_coronal.png")
            self.add_image_to_markdown(save_img_sag_cor, "Sagittal & Coronal Overlay")

    def convert_md_to_html(self):
        with open(self.markdown_pth, 'r', encoding='utf-8') as file:
            md_content = file.read()

        # Preprocess the markdown to wrap images and their titles in a container
        md_content = re.sub(
            r'^##### (.*?)\n\n!\[\1\]\((.*?)\)$',  # Match the description header followed by the image syntax
            r'<div class="img-container"><span class="img-title">\1</span><img src="\2" alt="\1"></div>',
            md_content,
            flags=re.MULTILINE  # This allows ^ and $ to match the start and end of each line
        )

        html_content = markdown.markdown(md_content)

        # Add CSS styles for images, their titles, and text
        styles = """
        <style>
            img {
                max-width: 90%;
                display: block;
            }
            .img-container {
                display: flex;
                align-items: center;
                margin: 10px 0;
            }
            .img-title {
                font-size: 1em;
                margin-right: 10px;
                width: 150px;  /* Fixed width for the title. Adjust as needed. */
                overflow: hidden;
                white-space: normal;  /* Allow line breaks */
            }
            body {
                font-size: 1.5em;
                font-family: Arial, sans-serif;
            }
        </style>
        """

        full_html = f"<!DOCTYPE html>\n<html>\n<head>{styles}</head>\n<body>{html_content}</body>\n</html>"

        with open(self.html_pth, 'w', encoding='utf-8') as file:
            file.write(full_html)







