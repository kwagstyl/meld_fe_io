import os
import shutil
import ants
import nibabel as nb


def ants_coregister_to_fixed(moving_file, ref_file, output_file, save_transform="", transform_type = 'SyN'):
    ''' Coregister a file to a fixed reference file and save transform and coregistered nifti file
    inputs:
        - moving_file: the file to coregister
        - ref_file: the reference file e.g MNI nifti
        - output_file: the path and name of the file to save
        - save_transform: the path and basename of the transform 
        - transform_type: the type of transform to apply

    '''
    fixed = ants.image_read(ref_file)
    moving = ants.image_read(moving_file)
    mytx = ants.registration(fixed=fixed , moving=moving, type_of_transform=transform_type)
    warped_moving = mytx['warpedmovout']
    nii_img = ants.to_nibabel(warped_moving)
    nb.save(nii_img, output_file)
    #TODO: save transform
    if save_transform != "":
        shutil.copy(mytx['fwdtransforms'][0], save_transform+'.nii.gz')
        shutil.copy(mytx['fwdtransforms'][1], save_transform+'.mat')


def ants_coregister_with_tranfsorm(moving_file,  ref_file, output_file, transform_file):
    fixed = ants.image_read(ref_file)
    moving = ants.image_read(moving_file)
    mytx = ants.apply_transforms(fixed=fixed, moving=moving, transformlist=[transform_file+'.nii.gz',transform_file+'.mat'])
    nii_img = ants.to_nibabel(mytx)
    nb.save(nii_img, output_file)