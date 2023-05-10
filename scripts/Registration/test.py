from displaymod import DisplayModalities
from registration import Registration


#H101
img1 = '/Users/niccolo/PycharmProjects/modality_overlay_vis/H101/sub-MELDH101P00073/anat/sub-MELDH101P00073_3T_preop_T1w.nii.gz'
img2 = '/Users/niccolo/PycharmProjects/modality_overlay_vis/H101/sub-MELDH101P00073/anat/sub-MELDH101P00073_3T_preop_FLAIR.nii.gz'
seg = '/Users/niccolo/PycharmProjects/modality_overlay_vis/H101/sub-MELDH101P00073/anat/sub-MELDH101P00073_FLAIR_roi.nii.gz'

# H101 case 2:
#img1 = '/Users/niccolo/PycharmProjects/modality_overlay_vis/H101/sub-MELDH101P00001/anat/sub-MELDH101P00001_3T_preop_T1w.nii.gz'
#img2 = '/Users/niccolo/PycharmProjects/modality_overlay_vis/H101/sub-MELDH101P00001/anat/sub-MELDH101P00001_3T_preop_FLAIR.nii.gz'
#seg = '/Users/niccolo/PycharmProjects/modality_overlay_vis/H101/sub-MELDH101P00001/anat/sub-MELDH101P00001_FLAIR_roi.nii.gz'



# H4
#img1 = '/Users/niccolo/PycharmProjects/modality_overlay_vis/H4/sub-MELDH4P0131/anat/sub-MELDH4P0131_3T_preop_T1w.nii.gz'
#img2 = '/Users/niccolo/PycharmProjects/modality_overlay_vis/H4/sub-MELDH4P0131/anat/sub-MELDH4P0131_3T_preop_FLAIR.nii.gz'
#seg =


registration_helper = Registration()
registration_helper.set_fixed_img(img1)
registration_helper.registation_trx(img2)

img2_reg = '/Users/niccolo/PycharmProjects/modality_overlay_vis/H101/sub-MELDH101P00073/anat/sub-MELDH101P00073_3T_preop_FLAIR_reg.nii.gz'
seg_reg = '/Users/niccolo/PycharmProjects/modality_overlay_vis/H101/sub-MELDH101P00073/anat/sub-MELDH101P00073_FLAIR_roi_reg.nii.gz'

registered_img_2 = registration_helper.transform(img2, img2_reg)
registered_seg = registration_helper.transform(seg, seg_reg)



# before registration:
modality_helper = DisplayModalities()
modality_helper.display_image_seg(img1, img2, seg=seg, superimpose=True, save_name="img_pre_reg", colormap='jet')  # colormap='gray'


# after registration:
modality_helper = DisplayModalities()
modality_helper.display_image_seg(img1, img2_reg, seg=seg_reg, superimpose=True, save_name="img_post_reg", colormap='jet')  # colormap='gray'

