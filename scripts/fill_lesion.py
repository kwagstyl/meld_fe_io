### call segment_fill.py

import os
import glob
from segment_fill import SegmentationFill

folder = '/home/mathilde/Documents/RDS/MELD_FE/DATA/MELD_H16/raw_data/data_meldFCD/MELD_H16_filled_2'

list_lesions = glob.glob(os.path.join(folder, '*','*', '*lesion_mask.nii.gz'))
print(list_lesions)

fill_helper = SegmentationFill()

for seg_pth in list_lesions:
    save_pth = seg_pth.split('.nii.gz')[0]+'_filled.nii.gz'
    fill_helper.fill_segmentation(seg_pth, save_pth)


