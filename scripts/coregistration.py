import os
import shutil
import ants
import nibabel as nb

def correct_bias_n4(input_file, output_file):
    img = ants.image_read(input_file)
    img_corrected = ants.n4_bias_field_correction(img)
    nii_img = ants.to_nibabel(img_corrected)
    nb.save(nii_img, output_file)

    
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
    if save_transform != "" :
        for transform in mytx['fwdtransforms']:
            if '.nii' in transform:
                file = save_transform+'.nii.gz'
            elif '.mat' in transform:
                file = save_transform+'.mat'
            shutil.copy(transform, file)



def ants_coregister_with_transform(moving_file,  ref_file, output_file, transform_file):
    fixed = ants.image_read(ref_file)
    moving = ants.image_read(moving_file)
    #load transform
    transformlist = []
    for transform in [transform_file+'.nii.gz',transform_file+'.mat']:
        if os.path.isfile(transform):
            transformlist.append(transform)
    mytx = ants.apply_transforms(fixed=fixed, moving=moving, transformlist=transformlist)
    nii_img = ants.to_nibabel(mytx)
    nb.save(nii_img, output_file)



