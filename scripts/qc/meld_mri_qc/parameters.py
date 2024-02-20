class Config:

    def __init__(self):

        site = 'H101'
        batch = 'controls'
        self.orig_bids_folder = f'/home/mathilde/Documents/RDS/MELD_FE/DATA/MELD_{site}/MELD_BIDS/'

        self.list_subjects = f'/home/mathilde/Documents/RDS/MELD_FE/DATA/MELD_{site}/MELD_BIDS_QC/list_subjects_{batch}.csv' #None
        
        # Saving locations:
        # for registered images:
        self.save_dir = f'/home/mathilde/Documents/RDS/MELD_FE/DATA/MELD_{site}/MELD_BIDS_QC'  # folder for saving images
        self.img_save_dir = f'/home/mathilde/Documents/RDS/MELD_FE/DATA/MELD_{site}/MELD_BIDS_QC/qc_images/'

        self.synth_save_dir = f'/home/mathilde/Documents/RDS/MELD_FE/DATA/MELD_{site}/MELD_BIDS_QC/synthseg/'  # None

        self.mask_in_flair = False

        self.t1_tail = "_preop_T1w.nii.gz"
        self.flair_tail = "_preop_FLAIR.nii.gz"
        self.t2_tail = "_preop_T2w.nii.gz"  # None
        self.t1_postop_tail = "_postop_T1w.nii.gz"

        self.mask_tail = "_lesion_mask.nii.gz"

        self.preop_dwi_tail = "_preop_DWI.nii.gz"
        self.preop_DWInegPE_tail = "_preop_DWInegPE.nii.gz"

        self.matrix_save_name = f"df_qc_{batch}.csv"

        self.markdown_title = "MELD_QC"
        self.markdown_file = f"image_gallery_{batch}.md"

        self.html_file = f"image_gallery_{batch}.html"

        self.use_synthseg = True





