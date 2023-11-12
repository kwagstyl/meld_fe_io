class Config:

    def __init__(self):

        self.orig_bids_folder = '/home/nmcconnell/rds/MELD_FE/DATA/MELD_H14/MELD_BIDS/'

        # Saving locations:
        # for registered images:
        self.save_dir = '/home/nmcconnell/project/qc_data/MELD_H14/QC/save_MELD'  # folder for saving images
        self.img_save_dir = '/home/nmcconnell/project/qc_data/MELD_H14/QC/save_MELD/qc_images/'

        self.synth_save_dir = '/home/nmcconnell/project/qc_data/MELD_H14/QC/save_MELD/synthseg/'  # None

        self.mask_in_flair = False

        self.t1_tail = "_preop_T1w.nii.gz"
        self.flair_tail = "_preop_FLAIR.nii.gz"
        self.t2_tail = "_preop_T2w.nii.gz"  # None
        self.t1_postop_tail = "_postop_T1w.nii.gz"

        self.mask_tail = "_lesion_mask.nii.gz"

        self.preop_dwi_tail = "_preop_DWI.nii.gz"
        self.preop_DWInegPE_tail = "_preop_DWInegPE.nii.gz"

        self.matrix_save_name = "matrix.csv"

        self.markdown_title = "MELD_QC"
        self.markdown_file = "image_gallery.md"

        self.html_file = "image_gallery.html"

        self.use_synthseg = True





