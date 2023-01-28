import os
import subprocess
import shlex

from parameters import Config


class Converter:

    """
    This class can be utilised to convert a provided list of HD16 format cases (via config) to BIDS format.

    Steps for the dataset conversion:
    1) complete the parameter list via the parameters.py file.
    2) call the main method via: hd16_bids_convert_main.py

    The class conducts the following steps:
    1) create new BIDS folder with appropriate name (if applicable via config)
    2) transfer respective .csv file (if not present)
    3) for each case it will:
        i) create its respective BIDS and anat folder
        ii) copy original .nii and .label volumetric files to anat location
        iii) convert .nii and .label files to .nii.gz

    Note: This class can be tailored in order to work with other new data cohorts if needed.
    """

    def __init__(self):

        config = Config()

        self.case_list = config.case_list  # List[str] - corresponding to HD16 case sub-folders
        self.orig_dir_pth = config.orig_dir_pth   # str - original HD16 data directory location
        self.new_dir_pth = config.new_dir_pth  # str - new BIDS data directory location
        self.orig_nii_root = config.orig_nii_root  # str - root name of .nii file in HD16

        self.case_anat = None  # path to individual case anat file

    @staticmethod
    def directory_validator(data_directory: str):
        """
        Validates that directory exists.
        :param data_directory: Directory points to where cases/csv file is e.g. ./pilot_dataset/MELD_H101
        """
        return os.path.exists(data_directory)

    def new_dir(self):
        """
        Creates new bids-format folder if non-existent
        """
        if not os.path.exists(self.new_dir_pth):

            command = f"mkdir {self.new_dir_pth}"
            command = shlex.split(command)
            subprocess.run(command, stdout=subprocess.PIPE, universal_newlines=True)

            print(f"BIDS directory succesfully created at: {self.new_dir_pth}")

    def transfer_csv(self):
        """
        Transfer the csv file to BIDS folder if not already present.
        """
        csv_name = os.path.basename(os.path.normpath(self.orig_dir_pth)) + "_participants_info.csv"
        new_csv_pth = os.path.join(self.new_dir_pth, csv_name)

        if not os.path.exists(new_csv_pth):
            old_csv_pth = os.path.join(self.orig_dir_pth, csv_name)

            command = f"scp {old_csv_pth} {new_csv_pth}"
            command = shlex.split(command)
            subprocess.run(command, stdout=subprocess.PIPE, universal_newlines=True)
            
            print(".csv file succesfully transferred.")

    @staticmethod
    def is_patient(case: str) -> bool:
        """
        Check if given case corresponds to a patient or control.
        :param case: HD16 case specific sub-folder name
        :return: True if case corresponds to patient
        """
        if "P" in case:
            return True
        else:
            return False

    def case_no_extract(self, case: str) -> str:
        """
        Extract case number e.g. "MELD_H16_P_0101" -> "0101"
        :param case: HD16 case specific sub-folder name
        :return: case number
        """
        return case.split(sep='_')[-1]

    @staticmethod
    def case_name_bidsconvert(case: str) -> str:
        """
        Convert to BIDS name e.g. "MELD_H16_P_0101"  ->  "sub-MELDH16P0101"
        :param case: HD16 case specific sub-folder name
        :return: BIDS specific case name
        """
        return "sub-" + case.replace("_", "")

    def case_loc_create(self, case: str):
        """
        Create BIDS case specific sub-folder folder and its respective anat sub-folder
        :param case: HD16 case specific sub-folder name
        """
        case_pth = os.path.join(self.new_dir_pth, self.case_name_bidsconvert(case))

        command = f"mkdir {case_pth}"
        command = shlex.split(command)
        subprocess.run(command, stdout=subprocess.PIPE, universal_newlines=True)

        self.case_anat = os.path.join(case_pth, "anat/")
        command = f"mkdir {self.case_anat}"
        command = shlex.split(command)
        subprocess.run(command, stdout=subprocess.PIPE, universal_newlines=True)

    def transfer_label(self, case: str):
        """
        Transfer old label file to new BIDS location while converting file name to BIDS format.
        NOTE: in HD16 label file is consistent for all cases i.e. fcd.label
        :param case: HD16 case specific sub-folder name
        """
        old_label_pth = os.path.join(self.orig_dir_pth, case, "fcd.label")
        new_label_pth = os.path.join(self.case_anat, self.case_name_bidsconvert(case) + "_3T_lesion_mask.label")

        command = f"scp {old_label_pth} {new_label_pth}"
        command = shlex.split(command)
        subprocess.run(command, stdout=subprocess.PIPE, universal_newlines=True)

    def transfer_nii(self, case: str):
        """
        Copy old anatomical .nii file to new BIDS location while converting old file name to BIDS.

        IMPORTANT NOTE: in HD16 folders have leading one in case number, however this is dropped in the orig .nii name.
        Also case number is one digit shorter. Hence this format must be consistent for this class method to work.
        e.g. MELD_H16_P_0103 has MELD_H16_3T_FCD_003.nii as respective nifti

        Further NOTE: for the BIDS name conversion, keeping the leading 1 and using the following conversion:
        MELD_H16_3T_FCD_003.nii -> sub-MELDH16P0103_3T_preop_T1w.nii.gz

        :param case: HD16 case specific sub-folder name
        """
        nii_name = self.orig_nii_root + "0" + self.case_no_extract(case)[-2:] + ".nii"  # e.g. MELD_H16_3T_FCD_003.nii
        old_label_pth = os.path.join(self.orig_dir_pth, case, nii_name)
        new_label_pth = os.path.join(self.case_anat, self.case_name_bidsconvert(case) + "_3T_preop_T1w.nii")

        command = f"scp {old_label_pth} {new_label_pth}"
        command = shlex.split(command)
        subprocess.run(command, stdout=subprocess.PIPE, universal_newlines=True)

    def transfer_files(self, case: str):
        """
        Transer both the .nii and .label files to corresponding BIDS sub-folder location
        :param case: HD16 case specific sub-folder name
        """
        self.transfer_label(case)
        self.transfer_nii(case)

    def convert_label(self, case: str):
        """
        Convert .label to .nii.gz using freesurfer (https://surfer.nmr.mgh.harvard.edu).
        Then delete the .label file.
        :param case: HD16 case specific sub-folder name
        """
        label = os.path.join(self.case_anat, self.case_name_bidsconvert(case) + "_3T_lesion_mask.label")
        temp = os.path.join(self.case_anat, self.case_name_bidsconvert(case) + "_3T_preop_T1w.nii")
        out = os.path.join(self.case_anat, self.case_name_bidsconvert(case) + "_3T_lesion_mask.nii.gz")

        command = f"mri_label2vol --label {label} --temp {temp} --o {out} --identity"
        command = shlex.split(command)
        subprocess.run(command, stdout=subprocess.PIPE, universal_newlines=True)

        command = f"rm {label}"
        command = shlex.split(command)
        subprocess.run(command, stdout=subprocess.PIPE, universal_newlines=True)

    def convert_nii(self, case: str):
        """
        Convert .nii to .nii.gz
        :param case: HD16 case specific sub-folder name
        """
        new_label_pth = os.path.join(self.case_anat, self.case_name_bidsconvert(case) + "_3T_preop_T1w.nii")
        command = f"gzip {new_label_pth}"
        command = shlex.split(command)
        subprocess.run(command, stdout=subprocess.PIPE, universal_newlines=True)

    def convert_files(self, case: str):
        """
        Convert both .label and the .nii files to required BIDS format
        :param case: HD16 case specific sub-folder name
        """
        self.convert_label(case)
        self.convert_nii(case)

    def case_convert(self, case: str):
        """
        Overall case specific converter
        :param case: HD16 case specific sub-folder name
        """
        self.case_loc_create(case)
        self.transfer_files(case)
        self.convert_files(case)

    def case_list_convert(self: str):
        """
        Convert all individual cases for all cases in self.case_list
        :return:
        """
        for case in self.case_list:
            self.case_convert(case)
            print(f"Completed conversion of case - {case}")


