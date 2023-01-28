import os
import pandas as pd
import json
import SimpleITK as sitk
import numpy as np
import matplotlib.pyplot as plt
import warnings


class SubjectLoader:
    """
    This is the subject loader class.

    Follow the following steps to get started:

    1) Create instance of class by providing a valid data cohort directory e.g. ./pilot_dataset/MELD_H101
    2) Provide a valid Subject ID using the self.subject_id = subject_id.
        Note: this must be same format as in csv file. If incorrect you will be prompted with valid potential values.
    3) Provide a valid modality using self.modality = modality.
        Note: If incorrect you will be prompted with valid potential values.

    Useful Helper Methods:

    i) self.cohort_ids() - provides a list of valid subject IDs for the provided directory.
    ii) self.list_possible_mods() - provides a list of valid imaging modalities for the subject_id.

    After completion of steps (1)-(3), one can make use of the following methods:
    (Refer to the relevant docstrings for more detailed information)

    # CSV specific Methods:

    i) self.cohort_data() - output entire cohort-wide data
    ii) self.demographic_features() - output callable features
    iii) self.present_demographic_features() - output features with non-null value for current subject_id
    iv) self.extract_demographic_variable(var) - output specific value of desired feature (var)


    # Imaging Modality Json Methods:

    i) self.output_json() - output entire json
    ii) self.list_json_vars() - output callable json features
    iii) self.extract_json_var(var) - output specific value of desired feature (var)

    # Image Visualisation Methdos:

    i) display_image_seg(display_seg=False, superimpose=False, x=None, y=None, z=None,
                         save_name=None, colormap='gray')

    """

    def __init__(self, data_directory: str):
        """
        :param data_directory: points to the cohort directory e.g. ./pilot_dataset/MELD_H101
        """

        self._data_directory = data_directory

        self._subject_id = None  # str - this needs to be inputted, call self.cohort_ids() for options
        self._modality = None  # str - imaging modality call self.list_possible_mods() for options

        self._csv_file = os.path.join(self._data_directory, os.path.basename(os.path.normpath(self._data_directory))
                                      + "_participants_info.csv")
        self._data_frame = pd.read_csv(self._csv_file)

        self.data_directory_check()

    @property
    def data_directory(self) -> str:
        """
        Outputs the current directory.
        :return: subject id e.g. MELD_H4_P_0028
        """
        return self._data_directory

    @data_directory.setter
    def data_directory(self, data_directory: str):
        """
        Set a new data directory. Also for new directory refresh the csv and data_frame properties.
        :param data_directory: Directory points to where cases/csv file is e.g. ./pilot_dataset/MELD_H101
        """
        self.directory_validator(data_directory)
        self._data_directory = data_directory

        self._csv_file = os.path.join(self._data_directory, os.path.basename(os.path.normpath(self._data_directory))
                                      + "_participants_info.csv")
        self._data_frame = pd.read_csv(self._csv_file)

    @staticmethod
    def directory_validator(data_directory: str):
        """
        Validates that directory exists.
        :param data_directory: Directory points to where cases/csv file is e.g. ./pilot_dataset/MELD_H101
        """
        if not os.path.exists(data_directory):
            raise NotADirectoryError("Provided directory does not exist, please enter valid directory.")

    def data_directory_check(self):
        """
        Validates the _data_directory property.
        """
        self.directory_validator(self._data_directory)

    @property
    def subject_id(self) -> str:
        """
        Outputs the current subject ID.
        :return: subject id e.g. MELD_H4_P_0028
        """
        return self._subject_id

    @subject_id.setter
    def subject_id(self, subject_id: str):
        """
        Set the subject id.
        :param subject_id: Subject id must be in the format listed in the csv file.
        """
        self.subject_id_validator(subject_id)
        self._subject_id = subject_id

    def subject_id_validator(self, subject_id: str):
        """
        Validates that subject id is contained within csv file for provided directory.
        :param subject_id: Subject id must be in the format listed in the csv file.
        """
        if subject_id is None:
            raise ValueError("No subject ID inputted."
                             f"Accepted IDs for provided directory are: {self.cohort_ids()}")

        elif type(subject_id) is not str:
            raise TypeError("Subject ID invalid. Must be a string type.")

        elif subject_id not in self.cohort_ids():
            raise NameError(f"Incorrect subject ID provided. Please provide a valid subject ID. "
                            f"Accepted IDs for provided directory are: {self.cohort_ids()}")

    def subject_id_check(self):
        """
        Validates the _subject_id property.
        """
        self.subject_id_validator(self._subject_id)

    @property
    def modality(self) -> str:
        """
        Outputs the imaging modality e.g. "3T_preop_T1w", "3T_preop_FLAIR"
        :return: imaging modality.
        """
        return self._modality

    @modality.setter
    def modality(self, modality: str):
        """
        Set the imaging modality.
        :param modality: imaging modality.
        """
        self.modality_validator(modality)
        self._modality = modality

    def modality_validator(self, modality):
        """
        Validated the modality.
        :param modality: imaging modality.
        """
        if modality is None:
            raise ValueError("No imaging modality inputted."
                             "Accepted modalities for provided subject id and directory are following: "
                             f"{self.list_possible_mods()}")
        if type(modality) is not str:
            raise TypeError("Modality invalid. Must be a string type.")

        if modality not in self.list_possible_mods():
            raise NameError("Incorrect subject modality provided for the subject id."
                            "Accepted modalities for provided subject id and directory are following: "
                            f"{self.list_possible_mods()}")

    def modality_check(self):
        """
        Validates the _modality property.
        """
        self.modality_validator(self._modality)

    def cohort_ids(self) -> list:
        """
        :return: All the cohort ids (str) from csv as a list.
        """
        return self._data_frame.id.values.tolist()

    def is_patient(self) -> bool:
        """
        Check if given case corresponds to a patient or control.
        :return: True if case corresponds to patient
        """
        self.subject_id_check()

        if "P" in self._subject_id:
            return True
        else:
            return False

    ######### CSV Specific: ############

    def cohort_data(self) -> pd.DataFrame:
        """
        :return: Output the entire csv file for provided directory in pandas dataframe format.
        """
        return self._data_frame

    def demographic_features(self) -> pd.DataFrame:
        """
        :return: Output entire row of csv dataframe for specific subject id
        """
        self.subject_id_check()
        return self._data_frame.loc[self._data_frame["id"] == self._subject_id]

    def present_demographic_features(self) -> pd.DataFrame:
        """
        :return: Output row of csv dataframe for specific subject id removing columns with null entries.
        """
        return self.demographic_features().dropna(axis=1)

    def extract_demographic_variable(self, var: str):
        """
        Extract a specific variable for the suject id (no longer of type dataframe)
        :param var: Variable from csv whose value should be returned.
        :return: Value of requested variable.
        """
        self.subject_id_check()
        try:
            return self._data_frame.loc[self._data_frame["id"] == self._subject_id, var].to_numpy()[0]
        except:
            raise NameError(f"Non-recognized variable name. Possible variable names include:"
                            f"{self._data_frame.columns.values.tolist()}")

    ########### Json Specific ###########

    def subject_id_to_bids_format(self) -> str:
        """
        Converts subject id namce from the csv format to bids format used in folder names.
        :return: Bids format name e.g. MELD_H4_P_0028 -> sub-MELDH4P0028
        """
        self.subject_id_check()
        return "sub-" + self._subject_id.replace("_", "")

    def case_pth_create(self) -> str:
        """
        :return: The case specific path, via joining directory with case specific bids folder name.
        """
        return os.path.join(self.data_directory, self.subject_id_to_bids_format())

    def case_dir_anat_create(self) -> str:
        """
        :return: The BIDS path to anat sub-folder for specific subject.
        """
        return os.path.join(self.case_pth_create(), "anat")

    def case_dir_dwi_create(self) -> str:
        """
        :return: The BIDS path to dwi sub-folder for specific subject.
        """
        return os.path.join(self.case_pth_create(), "dwi")

    def cohort_specifier(self) -> str:
        """
        Outputs the cohort which the subject ID originates from.
        Note: currently there are only 3 available cohorts: H101, H4, H16.
        :return: Subject id cohort.
        """
        self.subject_id_check()
        if "H101" in self._subject_id:
            return "H101"
        elif "H4" in self._subject_id:
            return "H4"
        elif "H16" in self._subject_id:
            return "H16"

    def list_possible_mods(self) -> list[str]:
        """
        :return: List of possible imaging modalities for provided subject id.
        """
        cohort = self.cohort_specifier()
        if cohort == "H101":
            return ["3T_preop_T1w", "3T_preop_FLAIR"]
        elif cohort == "H4":
            if self.is_patient():
                return ["3T_preop_T1w", "3T_preop_T2w", "3T_preop_FLAIR", "15T_postop_T1w",
                        "3T_preop_DWI", "3T_preop_DWInegPE"]
            elif not self.is_patient():
                return ["T1w", "FLAIR"]
        elif cohort == "H16":
            return ["3T_preop_T1w"]

    def mod_json_pth_finder(self) -> str:
        """
        :return: The path to the json file for the provided subject id and imaging modality type.
        """
        cohort = self.cohort_specifier()
        self.modality_check()

        if cohort == "H101" or cohort == "H16":
            # only anat
            anat_dir = self.case_dir_anat_create()
            return os.path.join(anat_dir, self.subject_id_to_bids_format() + "_" + self._modality + ".json")

        elif cohort == "H4":
            # anat and dwi
            if self._modality in ["3T_preop_DWI", "3T_preop_DWInegPE"]:
                dwi_dir = self.case_dir_dwi_create()
                return os.path.join(dwi_dir, self.subject_id_to_bids_format() + "_" + self._modality + ".json")

            elif self._modality in ["3T_preop_T1w", "3T_preop_T2w", "3T_preop_FLAIR", "15T_postop_T1w"]:
                anat_dir = self.case_dir_anat_create()
                return os.path.join(anat_dir, self.subject_id_to_bids_format() + "_" + self._modality + ".json")

    def json_pth_exists(self) -> bool:
        """
        :return: True if json path from self.mod_json_pth_finder exists.
        """
        return os.path.exists(self.mod_json_pth_finder())

    def json_pth_validator(self):
        """
        Validates the json path from mod_json_pth_finder. Raises specific errors otherwise.
        """
        if not self.json_pth_exists() and not self.is_patient() and self.cohort_specifier() == "H4":
            raise FileNotFoundError("Json file does not exist. Reason being H4 has no json for control patients.")

        if not self.json_pth_exists() and self.cohort_specifier() == "H16":
            raise FileNotFoundError("Json file does not exist. "
                                    "Reason being H16 cases currently do not have associated json.")

        elif not self.json_pth_exists():
            raise FileNotFoundError("Json file does not exist. Check the case folder for naming error.")

    def read_json(self) -> dict:
        """
        Converts the json file for the selected imaging modality/ subject id to a dictionary.
        :return: returns json as dictionary.
        """
        self.json_pth_validator()
        f = open(self.mod_json_pth_finder())
        data = json.load(f)
        f.close()
        return data

    def json_var_validator(self, var: str):
        """
        Validated whether inputted variable exists in the json file.
        :param var: Callable variable from json file.
        """
        self.json_pth_validator()
        if var not in self.list_json_vars():
            raise NameError("Provided variable not present in the json. "
                            f"Callable variables include: {self.list_json_vars()}")

    ##### Key json commands ####

    def output_json(self) -> dict:
        """
        Outputs the json file for the selected imaging modality/ subject id in a dictionary format.
        """
        self.json_pth_validator()
        return self.read_json()

    def list_json_vars(self) -> list:
        """
        :return: List of callable json variables for specific imaging modality/ subject id.
        """
        self.json_pth_validator()
        return list(self.read_json().keys())

    def extract_json_var(self, var):
        """
        Extracts the value form the json file for the specific imaging modality/ subject id, corresponding to the
        requested variable.
        :param var: requested variable of the json.
        :return: json variable value.
        """
        self.json_pth_validator()
        self.json_var_validator(var)
        return self.read_json()[var]


    ########### Visualisation ###########

    def img_pth_finder(self):
        """
        :return: The path to the image nii.gz file for the provided subject id/ imaging modality.
        :return: path to image file.
        """
        cohort = self.cohort_specifier()

        if cohort == "H101" or cohort == "H16":
            anat_dir = self.case_dir_anat_create()  # only anat
            return os.path.join(anat_dir, self.subject_id_to_bids_format() + "_" + self._modality + ".nii.gz")

        elif cohort == "H4":  # anat or dwi
            if self._modality in ["3T_preop_DWI", "3T_preop_DWInegPE"]:
                dwi_dir = self.case_dir_dwi_create()
                return os.path.join(dwi_dir, self.subject_id_to_bids_format() + "_" + self._modality + ".nii.gz")

            elif self._modality in ["3T_preop_T1w", "3T_preop_T2w", "3T_preop_FLAIR", "15T_postop_T1w"]:
                anat_dir = self.case_dir_anat_create()
                return os.path.join(anat_dir, self.subject_id_to_bids_format() + "_" + self._modality + ".nii.gz")

    def seg_pth_finder(self) -> str:
        """
        :return: The path to the segmenation label file for the provided subject id.
        Note: Assuming there is only 1 seg file per cohort.
        :return: path to label file.
        """
        cohort = self.cohort_specifier()
        anat_dir = self.case_dir_anat_create()

        if cohort == "H101":
            return os.path.join(anat_dir, self.subject_id_to_bids_format() + "_FLAIR_roi.nii.gz")

        elif cohort == "H4" or cohort == "H16":
            return os.path.join(anat_dir, self.subject_id_to_bids_format() + "_3T_lesion_mask.nii.gz")

        elif cohort == "H16":
            return os.path.join(anat_dir, self.subject_id_to_bids_format() + "_3T_lesion_mask.nii.gz")

    @staticmethod
    def coords_extract(seg_array: np.array) -> tuple:
        """
        Automatically searches through the provided rgb seg array along the x,y, and z axes.
        Chooses x coord with largest segmentation label area throughout the yz planes.
        Chooses y coord with largest segmentation label area throughout the xz planes
        Chooses z coord with largest segmentation label area throughout the xy planes

        :param seg_array: rgb np array corresponding to 1 class segmentation file.
        :return: tuple of chosen coordinated.
        """
        x_coord = None
        x_size = 0
        y_coord = None
        y_size = 0
        z_coord = None
        z_size = 0

        for i in range(0, seg_array.shape[0]):
            if len(seg_array[i,:,:,1].nonzero()[0]) > x_size:
                x_coord = i

        for i in range(0, seg_array.shape[1]):
            if len(seg_array[:,i,:,1].nonzero()[0]) > y_size:
                y_coord = i

        for i in range(0, seg_array.shape[2]):
            if len(seg_array[:,:,i,1].nonzero()[0]) > z_size:
                z_coord = i

        return x_coord, y_coord, z_coord

    @staticmethod
    def wl_to_lh(window: float, level: float) -> tuple:
        """
        Helper function for colour limits.
        :param window:
        :param level:
        :return:
        """
        low = level - window/2
        high = level + window/2
        return low, high

    def display_image_seg(self, display_seg=False, superimpose=False, x=None, y=None, z=None,
                          save_name=None, colormap='gray'):
        """
        Method to save orthogonal slices of 3D medical image.
        Provides 3 viewing options:
        1) MRI only  [using display_seg=False]
        2) Seperate MRI + Segmentation (if applicable) [using display_seg=True, superimpose=False]
        3) Seperate MRI + Superimposed Segmentation (if applicable) [using display_seg=True, superimpose=True]

        Provides options to select x, y, z axis positions although will select these otherwise.

        Also allows saving via save_name variable.

        Code inspired by ML for Imaging module by Dr Ben Glocker.
        (refer: https://gitlab.doc.ic.ac.uk/bglocker/rcs-summer-school/-/blob/master/utils/image_viewer.py)
        note: ! pip install SimpleITK==1.2.4

        :param display_seg: bool - True if want segmentation displayed
        :param superimpose: bool - True if want segmentation separately superimposed on MRI
        :param x: int - choosen x coordinate for yz plane
        :param y: int - choosen y coordinate for xz plane
        :param z: int - choosen z coordinate for xy plane
        :param save_name: str - name of saved file if requested.
        :param colormap: str - chosen colormap.
        """

        if not self.is_patient() and display_seg:
            display_seg = False
            warnings.warn(f"Note: Chosen subject ID ({self._subject_id}) is for control case which therefore has no associated ROI.")

        img_pth = self.img_pth_finder()
        seg_pth = self.seg_pth_finder()

        img = sitk.ReadImage(img_pth, sitk.sitkFloat32)  # convert to sitk object
        seg = sitk.LabelToRGB(sitk.ReadImage(seg_pth, sitk.sitkInt64))

        img_array = sitk.GetArrayFromImage(img)
        seg_array = sitk.GetArrayFromImage(seg)

        if x is None or y is None or z is None:
            coords = self.coords_extract(seg_array)
            if x is None:
                x = coords[0]
            if y is None:
                y = coords[1]
            if z is None:
                z = coords[2]

        window = np.max(img_array) - np.min(img_array)

        level = window / 2 + np.min(img_array)

        low, high = self.wl_to_lh(window, level)

        # Display the orthogonal slices
        if not display_seg:
            fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(10, 4))

            ax1.imshow(img_array[x,:,:], cmap=colormap, clim=(low, high))
            ax2.imshow(img_array[:,y,:], origin='lower', cmap=colormap, clim=(low, high))
            ax3.imshow(img_array[:,:,z], origin='lower', cmap=colormap, clim=(low, high))

        else:

            if not superimpose:
                fig, ((ax1, ax2, ax3), (ax4, ax5, ax6)) = plt.subplots(2, 3, figsize=(10, 4))

                ax1.imshow(img_array[x,:,:], cmap=colormap, clim=(low, high))
                ax2.imshow(img_array[:,y,:], origin='lower', cmap=colormap, clim=(low, high))
                ax3.imshow(img_array[:,:,z], origin='lower', cmap=colormap, clim=(low, high))

                ax4.imshow(seg_array[x,:,:], cmap=colormap, clim=(low, high))
                ax5.imshow(seg_array[:,y,:], origin='lower', cmap=colormap, clim=(low, high))
                ax6.imshow(seg_array[:,:,z], origin='lower', cmap=colormap, clim=(low, high))

            else:
                fig, ((ax1, ax2, ax3), (ax4, ax5, ax6)) = plt.subplots(2, 3, figsize=(10, 4))

                ax1.imshow(img_array[x,:,:], cmap=colormap, clim=(low, high))

                ax2.imshow(img_array[:,y,:], origin='lower', cmap=colormap, clim=(low, high))

                ax3.imshow(img_array[:,:,z], origin='lower', cmap=colormap, clim=(low, high))

                ax4.imshow(img_array[x,:,:], cmap=colormap, clim=(low, high))
                ax4.imshow(seg_array[x,:,:], cmap="jet", alpha=0.2, clim=(low, high))

                ax5.imshow(img_array[:,y,:], origin='lower', cmap=colormap, clim=(low, high))
                ax5.imshow(seg_array[:,y,:], origin='lower', cmap="jet", alpha=0.2, clim=(low, high))

                ax6.imshow(img_array[:,:,z], origin='lower', cmap=colormap, clim=(low, high))
                ax6.imshow(seg_array[:,:,z], origin='lower', cmap="jet", alpha=0.2, clim=(low, high))

        if save_name is not None:
            plt.savefig(f"{save_name}", dpi=600)

        self.display_modality_warning()

        plt.show()

    def display_modality_warning(self):
        """
        Warns if modality an segmentation map are of different types.
        """
        cohort = self.cohort_specifier()

        if cohort == "H101" and self._modality != "3T_preop_FLAIR":
            warnings.warn(f"Note: For H101 ROI is in FLAIR which is different to specified modality ({self._modality}).")

