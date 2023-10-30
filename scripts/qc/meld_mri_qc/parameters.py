class Config:

    def __init__(self):

        ### Note, might want to add a list of subjects

        self.orig_bids_folder = '/Users/niccolo/Documents/UCL/Autumn_2023/meld_mri_qc/Data'

        # Saving locations:
        # for registered images
        self.save_dir = '/Users/niccolo/Documents/UCL/Autumn_2023/meld_mri_qc/gg'  # folder for saving images
        self.img_save_dir = '/Users/niccolo/Documents/UCL/Autumn_2023/meld_mri_qc/gg/qc_images/'

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





# worth having qc photo of postop no mask?
