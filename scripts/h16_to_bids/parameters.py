class Config:

    def __init__(self):

        self.case_list = [
                        # "MELD_H16_P_0101","MELD_H16_P_0102","MELD_H16_P_0103","MELD_H16_P_0104","MELD_H16_P_0105",
                        #   "MELD_H16_P_0108","MELD_H16_P_0109","MELD_H16_P_0110","MELD_H16_P_0111","MELD_H16_P_0112",
                        #   "MELD_H16_P_0113","MELD_H16_P_0114","MELD_H16_P_0115","MELD_H16_P_0116","MELD_H16_P_0117",
                        #   "MELD_H16_P_0118","MELD_H16_P_0120","MELD_H16_P_0121","MELD_H16_P_0122","MELD_H16_P_0123",
                        #   "MELD_H16_P_0124","MELD_H16_P_0126","MELD_H16_P_0128",
                          # "MELD_H16_P_0133",
                          "MELD_H16_P_0134",
                          "MELD_H16_P_0139",
                          # "MELD_H16_P_0142","MELD_H16_P_0143","MELD_H16_P_0144","MELD_H16_P_0145",
                          # "MELD_H16_P_0148"
                          ]  
                          # list of strings corresponding to HD16 case sub-folders/csv ids
                          # Note one can use the subject_loader class to list out cases contained in csv. 
        self.orig_dir_pth = "/home/mathilde/Documents/RDS/MELD_FE/DATA/MELD_H16/raw_data/data_meldFCD/MELD_H16"  # str - original HD16 data directory location

        self.new_dir_pth = "/home/mathilde/Documents/RDS/MELD_FE/DATA/MELD_H16/raw_data/data_meldFCD/MELD_H16_filled_2"  # str - new BIDS data directory location

        self.orig_root = "brain.mgz"  # str - root name of .nii or .mgz file in HD16


# Important Note: Ensure Freesurfer is activated e.g.:
# export FREESURFER_HOME=/rds-d5/user/hpcmcco1/hpc-work/freesurfer
# source $FREESURFER_HOME/SetUpFreeSurfer.sh