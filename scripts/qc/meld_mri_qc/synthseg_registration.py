import subprocess
import os
import numpy as np
import SimpleITK as sitk


class SynthSegRegistration:

    def __init__(self):

        self.ref = None
        self.ref_seg = None

        self.flo = None
        self.flo_seg = None

        self.fwd_field = None

        self.reg_save_dir = None

        self.synth_save_dir = None
        self.save_moving_img_pth = None

        self.synthsr_pth = None

        self.flo_seg_warp = None

        self.t1_seg_exist = False

        self.t1_suffix = "preop_T1w_synthseg.nii.gz"  # change if needed

        self.is_postop = False

    def set_params(self, fixed_img_pth, moving_img_pth, save_moving_img_pth,
                   synth_save_dir, fwd_field_pth, is_postop=False):

        self.ref = fixed_img_pth
        self.flo = moving_img_pth

        self.save_moving_img_pth = save_moving_img_pth

        self.synth_save_dir = synth_save_dir

        self.fwd_field = fwd_field_pth  # fwdfield.nii.gz

        self.is_postop = is_postop

        self.t1_seg_exist = any(fname.endswith(self.t1_suffix) for fname in os.listdir(self.synth_save_dir))

    def synthsr(self):
        
        cmnd = f"mri_synthsr --i {self.flo} --o {self.synth_save_dir}"
        # print(cmnd)
        subprocess.run(cmnd.split())

        self.synthsr_pth = os.path.join(self.synth_save_dir,
                                        os.path.basename(self.flo)).replace(".nii.gz", "_synthsr.nii.gz")
        # example: sub-MELDH14P0013_3T_postop_T1w.nii.gz  -> sub-MELDH14P0013_3T_postop_T1w_synthsr.nii.gz

    def synthseg(self, input_flo_img):
        self.ref_seg = os.path.join(self.synth_save_dir,
                                        os.path.basename(self.ref)).replace(".nii.gz", "_synthseg.nii.gz")
        self.flo_seg = os.path.join(self.synth_save_dir,
                                        os.path.basename(input_flo_img)).replace(".nii.gz", "_synthseg.nii.gz")

        if not self.t1_seg_exist:
            cmnd = f"mri_synthseg --i {self.ref} --o {self.synth_save_dir} --parc --robust --resample {self.synth_save_dir}"
            subprocess.run(cmnd.split())  # all extras saved to synth_sr_folder

            cmnd = f"mri_synthseg --i {input_flo_img} --o {self.synth_save_dir} --parc --robust --resample {self.synth_save_dir}"
            subprocess.run(cmnd.split())  # all extras saved to synth_sr_folder
  
        else:
            cmnd = f"mri_synthseg --i {input_flo_img} --o {self.synth_save_dir} --parc --robust --resample {self.synth_save_dir}"
            subprocess.run(cmnd.split())  # all extras saved to synth_sr_folder

    def easyreg(self):
        if not self.is_postop:
            cmnd = f"mri_easyreg --ref {self.ref} --flo {self.flo} \
            --ref_seg {self.ref_seg} --flo_seg {self.flo_seg} \
            --fwd_field {self.fwd_field}"
            subprocess.run(cmnd.split())

        else:
            cmnd = f"mri_easyreg --ref {self.ref} --flo {self.synthsr_pth} \
            --ref_seg {self.ref_seg} --flo_seg {self.flo_seg} \
            --fwd_field {self.fwd_field}"
            subprocess.run(cmnd.split())

    def easywarp(self):
        # if not self.is_postop:
        # use field to warp vol
        cmnd = f"mri_easywarp --i {self.flo} --o {self.save_moving_img_pth} \
        --field {self.fwd_field} --nearest"
        subprocess.run(cmnd.split())

        # produce final warped seg
        # note: all outputs are at 1mm ... hence t1seg may differ in dimension from actual t1
        # hence now will produce segmentation of transformed image by re-executing segmentation on transformed image.
        self.flo_seg_warp = os.path.join(self.synth_save_dir,
                                            os.path.basename(self.flo)).replace(".nii.gz", "_synthseg_warp.nii.gz")
        cmnd = f"mri_synthseg --i {self.save_moving_img_pth} --o {self.flo_seg_warp} --parc"
        subprocess.run(cmnd.split())  # all extras saved to synth_sr_folder

        # else:
        #     cmnd = f"mri_easywarp --i {self.synthsr_pth} --o {self.save_moving_img_pth} \
        #     --field {self.fwd_field} --nearest"
        #     subprocess.run(cmnd.split())

        #     # produce final warped seg
        #     # note: all outputs are at 1mm ... hence t1seg may differ in dimension from actual t1
        #     # hence now will produce segmentation of transformed image by re-executing segmentation on transformed image.
        #     self.flo_seg_warp = os.path.join(self.synth_save_dir,
        #                                      os.path.basename(self.synthsr_pth)).replace(".nii.gz", "_synthseg_warp.nii.gz")
        #     cmnd = f"mri_synthseg --i {self.save_moving_img_pth} --o {self.flo_seg_warp} --parc"
        #     subprocess.run(cmnd.split())  # all extras saved to synth_sr_folder

    def register(self, fixed_img_pth, moving_img_pth, save_moving_img_pth,
                 synth_save_dir, fwd_field_pth, is_postop=False):

        self.set_params(fixed_img_pth, moving_img_pth, save_moving_img_pth,
                        synth_save_dir, fwd_field_pth, is_postop)

        self.synthsr() if is_postop else None
        self.synthseg(self.synthsr_pth) if is_postop else self.synthseg(self.flo)
        self.easyreg()
        self.easywarp()
        return self.dice_calc()

    def calculate_dice(self, volume1, volume2, label):
        intersection = np.sum((volume1 == label) & (volume2 == label))
        volume1_count = np.sum(volume1 == label)
        volume2_count = np.sum(volume2 == label)

        # Calculate Dice score
        dice = (2. * intersection) / (volume1_count + volume2_count)
        return dice

    def dice_calc(self):
        volume1_sitk = sitk.ReadImage(self.ref_seg)
        volume2_sitk = sitk.ReadImage(self.flo_seg_warp)

        volume1_np = sitk.GetArrayFromImage(volume1_sitk)
        volume2_np = sitk.GetArrayFromImage(volume2_sitk)

        # Assuming the volumes contain the same set of labels, we can get the unique labels from one of the volumes
        labels = np.unique(volume1_np)

        dice_scores = [round(self.calculate_dice(volume1_np, volume2_np, label), 3) for label in labels if label != 0]

        dice_average = round(np.mean(dice_scores), 3)
        dice_stdev = round(np.std(dice_scores), 3)

        return dice_scores, dice_average, dice_stdev


