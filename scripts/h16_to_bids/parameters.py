class Config:

    def __init__(self):

        self.case_list = ["MELD_H16_P_0101", "MELD_H16_P_0103", "MELD_H16_P_0105",
                          "MELD_H16_P_0102", "MELD_H16_P_0104"]  
                          # list of strings corresponding to HD16 case sub-folders/csv ids
                          # Note one can use the subject_loader class to list out cases contained in csv. 

        self.orig_dir_pth = "/home/hpcmcco1/trial_data/pilot_dataset/MELD_H16_C"  # str - original HD16 data directory location

        self.new_dir_pth = "/home/hpcmcco1/trial_data/pilot_dataset/MELD_H16_BIDS/"  # str - new BIDS data directory location

        self.orig_nii_root = "MELD_H16_3T_FCD_"  # str - root name of .nii file in HD16


# Important Note: Ensure Freesurfer is activated e.g.:
# export FREESURFER_HOME=/rds-d5/user/hpcmcco1/hpc-work/freesurfer
# source $FREESURFER_HOME/SetUpFreeSurfer.sh