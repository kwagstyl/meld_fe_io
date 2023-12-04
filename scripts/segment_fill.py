import numpy as np
import SimpleITK as sitk
from scipy.ndimage import binary_dilation, binary_erosion, gaussian_filter
from scipy.ndimage import label
from scipy.ndimage import sum as ndi_sum


class SegmentationFill:
    """"""
    def __init__(self):

        self.orig_sitk_seg = None
        self.seg_array = None
        self.sitk_seg = None

    def get_sitk_array(self, seg_pth):

        self.orig_sitk_seg = sitk.ReadImage(seg_pth, sitk.sitkInt8)
        self.seg_array = sitk.GetArrayFromImage(self.orig_sitk_seg)

    def fill_3d(self, iterations=10, sigma=1):
        # Convert to integer and add a border of zeros around the array
        arr = np.pad(self.seg_array.astype(int), pad_width=1, mode='constant', constant_values=0)

        # Dilate the array to close small holes in the boundary
        dilated = binary_dilation(arr, iterations=iterations)

        # Make a copy of the dilated array and invert it
        inverse = 1 - dilated.copy()

        # Label each group of connected voxels in the 3D grid
        labeled_array, num_features = label(inverse)

        # Find the label of the largest component
        sizes = ndi_sum(inverse, labeled_array, range(num_features + 1))
        max_label = np.argmax(sizes)

        # Set all voxels with this label to zero in the dilated array
        dilated[labeled_array == max_label] = 0

        # Erode the dilated array to restore the original shape of the object
        filled = binary_erosion(dilated, iterations=iterations)

        # Apply Gaussian smoothing to the filled array
        filled = gaussian_filter(filled.astype(float), sigma=sigma)

        # Remove the border and convert back to integer
        filled = filled[1:-1, 1:-1, 1:-1] >= 0.05
        filled = filled.astype(int)

        return filled

    def fill_segmentation(self, seg_pth, save_pth):

        self.get_sitk_array(seg_pth)

        self.sitk_seg = sitk.GetImageFromArray(self.fill_3d())

        self.sitk_seg.SetDirection(self.orig_sitk_seg.GetDirection())
        self.sitk_seg.SetSpacing(self.orig_sitk_seg.GetSpacing())
        self.sitk_seg.SetOrigin(self.orig_sitk_seg.GetOrigin())
        self.sitk_seg.SetDirection(self.orig_sitk_seg.GetDirection())

        self.sitk_seg = sitk.Cast(self.sitk_seg, sitk.sitkUInt16)

        sitk.WriteImage(self.sitk_seg, save_pth)


# Usage:
# fill_helper = SegmentationFill()
# fill_helper.fill_segmentation(seg_pth, save_pth)

