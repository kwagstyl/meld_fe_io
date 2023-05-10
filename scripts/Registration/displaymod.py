import os
import SimpleITK as sitk
import numpy as np
import matplotlib.pyplot as plt
import warnings


class DisplayModalities:
    """
    """
    def __init__(self):
        pass

    @staticmethod
    def path_validator(path: str):
        """
        Validates that directory exists.
        :param path: path to img
        """
        if not os.path.exists(path):
            raise NotADirectoryError(f"Provided img path {path} does not exist, please enter valid path.")

    @staticmethod
    def coords_extract(array: np.array) -> tuple:
        """
        Returns midpoint coords of array
        :param seg_array: rgb np array corresponding to 1 class segmentation file.
        :return: tuple of chosen coordinates.
        """

        return int(array.shape[0]/2), int(array.shape[1]/2), int(array.shape[2]/2)


    @staticmethod
    def coords_seg_extract(seg_array: np.array) -> tuple:
        """
        Automatically searches through the provided rgb seg array along the x,y, and z axes.
        Chooses x coord with largest segmentation label area throughout the yz planes.
        Chooses y coord with largest segmentation label area throughout the xz planes
        Chooses z coord with largest segmentation label area throughout the xy planes
        :param seg_array: rgb np array corresponding to 1 class segmentation file.
        :return: tuple of chosen coordinated.
        """
        x_coord = None
        x_size = 0
        y_coord = None
        y_size = 0
        z_coord = None
        z_size = 0

        for i in range(0, seg_array.shape[0]):
            if len(seg_array[i,:,:,1].nonzero()[0]) > x_size:
                x_coord = i

        for i in range(0, seg_array.shape[1]):
            if len(seg_array[:,i,:,1].nonzero()[0]) > y_size:
                y_coord = i

        for i in range(0, seg_array.shape[2]):
            if len(seg_array[:,:,i,1].nonzero()[0]) > z_size:
                z_coord = i

        return x_coord, y_coord, z_coord



    def display_image_seg(self, img1, img2, seg=None, superimpose=False, x=None, y=None, z=None,
                          save_name=None, colormap='gray'): #'jet'
        """
        Function to save orthogonal slices of 3D medical image.
        Provides 2 viewing options:
        1) Seperate MRIs only - display img1, and img2
        2) Seperate MRIs + superimposed MRIs - display img1, img2, superimposed img1, img2, img1/img2

        Provides options to select x, y, z axis positions although will automatically select midpoint img1
        if coordinates not provided otherwise.

        Allows saving via save_name variable.

        note: ! pip install SimpleITK==1.2.4

        :param img1: str - path to img 1
        :param img2: str - path to img 2
        :param superimpose: bool - True if want segmentation separately superimposed on MRI
        :param x: int - choosen x coordinate for yz plane
        :param y: int - choosen y coordinate for xz plane
        :param z: int - choosen z coordinate for xy plane
        :param save_name: str - name of saved file if requested.
        :param colormap: str - chosen colormap.
        """

        self.path_validator(img1)
        self.path_validator(img2)

        img1_array = sitk.GetArrayFromImage(sitk.ReadImage(img1, sitk.sitkFloat32))  # convert to sitk object
        img2_array = sitk.GetArrayFromImage(sitk.ReadImage(img2, sitk.sitkFloat32))  # convert to sitk object

        if img1_array.shape[0:3] != img2_array.shape[0:3]:
            warnings.warn(f"CAUTION: There is an array size mismatch between the MR volume, {img1_array.shape}, and {img2_array.shape}."
                          f"This may affect acuracy of overlapped visualisation.")

        print(img1_array.shape)
        print(img2_array.shape)


       # window = np.max(img1_array) - np.min(img1_array)
        #level = window / 2 + np.min(img1_array)
        #low, high = self.wl_to_lh(window, level)

        if seg is None:
            if x is None or y is None or z is None:
                coords = self.coords_extract(img1_array)
                if x is None:
                    x = coords[0]
                if y is None:
                    y = coords[1]
                if z is None:
                    z = coords[2]

            if not superimpose:
                fig, ((ax1, ax2, ax3), (ax4, ax5, ax6)) = plt.subplots(2, 3, figsize=(10, 4))

                ax1.imshow(img1_array[x,:,:], cmap='gray')
                ax2.imshow(img1_array[:,y,:], origin='lower', cmap='gray')
                ax3.imshow(img1_array[:,:,z], origin='lower', cmap='gray')

                ax4.imshow(img2_array[x,:,:], cmap='gray')
                ax5.imshow(img2_array[:,y,:], origin='lower', cmap='gray')
                ax6.imshow(img2_array[:,:,z], origin='lower', cmap='gray')

                ax1.set_xticks([])
                ax1.set_yticks([])
                ax2.set_xticks([])
                ax2.set_yticks([])
                ax3.set_xticks([])
                ax3.set_yticks([])
                ax4.set_xticks([])
                ax4.set_yticks([])
                ax5.set_xticks([])
                ax5.set_yticks([])
                ax6.set_xticks([])

            else:
                fig, ((ax1, ax2, ax3), (ax4, ax5, ax6), (ax7, ax8, ax9)) = plt.subplots(3, 3, figsize=(10, 4))

                ax1.imshow(img1_array[x,:,:], cmap='gray')
                ax2.imshow(img1_array[:,y,:], origin='lower', cmap='gray')
                ax3.imshow(img1_array[:,:,z], origin='lower', cmap='gray')

                ax4.imshow(img2_array[x,:,:], cmap='gray')
                ax5.imshow(img2_array[:,y,:], origin='lower', cmap='gray')
                ax6.imshow(img2_array[:,:,z], origin='lower', cmap='gray')

                ax7.imshow(img1_array[x,:,:], cmap='gray')
                ax7.imshow(img2_array[x,:,:], cmap=colormap, alpha=0.3)

                ax8.imshow(img1_array[:,y,:], origin='lower', cmap='gray')
                ax8.imshow(img2_array[:,y,:], origin='lower', cmap=colormap, alpha=0.3)

                ax9.imshow(img1_array[:,:,z], origin='lower', cmap='gray')
                ax9.imshow(img2_array[:,:,z], origin='lower', cmap=colormap, alpha=0.3)

                ax1.set_xticks([])
                ax1.set_yticks([])
                ax2.set_xticks([])
                ax2.set_yticks([])
                ax3.set_xticks([])
                ax3.set_yticks([])
                ax4.set_xticks([])
                ax4.set_yticks([])
                ax5.set_xticks([])
                ax5.set_yticks([])
                ax6.set_xticks([])
                ax6.set_yticks([])
                ax7.set_xticks([])
                ax7.set_yticks([])
                ax8.set_xticks([])
                ax8.set_yticks([])
                ax9.set_xticks([])
                ax9.set_yticks([])

        else:
            self.path_validator(seg)
            seg_array = sitk.GetArrayFromImage(sitk.LabelToRGB(sitk.ReadImage(seg, sitk.sitkInt64)))

            if x is None or y is None or z is None:
                coords = self.coords_seg_extract(seg_array)
                if x is None:
                    x = coords[0]
                if y is None:
                    y = coords[1]
                if z is None:
                    z = coords[2]

            if not superimpose:  # note if seg is provided, seg is always sueperimosed
                fig, ((ax1, ax2, ax3), (ax4, ax5, ax6)) = plt.subplots(2, 3, figsize=(10, 4))

                ax1.imshow(img1_array[x,:,:], cmap='gray')
                ax1.imshow(seg_array[x,:,:], origin='lower', cmap='jet', alpha=0.3)
                ax2.imshow(img1_array[:,y,:], origin='lower', cmap='gray')
                ax2.imshow(seg_array[:,y,:], origin='lower', cmap='jet', alpha=0.3)
                ax3.imshow(img1_array[:,:,z], origin='lower', cmap='gray')
                ax3.imshow(seg_array[:,:,z], origin='lower', cmap='jet', alpha=0.3)

                ax4.imshow(img2_array[x,:,:], cmap='gray')
                ax4.imshow(seg_array[x,:,:], origin='lower', cmap='jet', alpha=0.3)
                ax5.imshow(img2_array[:,y,:], origin='lower', cmap='gray')
                ax5.imshow(seg_array[:,y,:], origin='lower', cmap='jet', alpha=0.3)
                ax6.imshow(img2_array[:,:,z], origin='lower', cmap='gray')
                ax6.imshow(seg_array[:,:,z], origin='lower', cmap='jet', alpha=0.3)

                ax1.set_xticks([])
                ax1.set_yticks([])
                ax2.set_xticks([])
                ax2.set_yticks([])
                ax3.set_xticks([])
                ax3.set_yticks([])
                ax4.set_xticks([])
                ax4.set_yticks([])
                ax5.set_xticks([])
                ax5.set_yticks([])
                ax6.set_xticks([])
                ax6.set_yticks([])

            else:
                fig, ((ax1, ax2, ax3), (ax4, ax5, ax6), (ax7, ax8, ax9)) = plt.subplots(3, 3, figsize=(10, 4))

                ax1.imshow(img1_array[x,:,:], cmap='gray')
                ax1.imshow(seg_array[x,:,:], origin='lower', cmap='jet', alpha=0.3)
                ax2.imshow(img1_array[:,y,:], origin='lower', cmap='gray')
                ax2.imshow(seg_array[:,y,:], origin='lower', cmap='jet', alpha=0.3)
                ax3.imshow(img1_array[:,:,z], origin='lower', cmap='gray')
                ax3.imshow(seg_array[:,:,z], origin='lower', cmap='jet', alpha=0.3)

                ax4.imshow(img2_array[x,:,:], cmap='gray')
                ax4.imshow(seg_array[x,:,:], origin='lower', cmap='jet', alpha=0.3)
                ax5.imshow(img2_array[:,y,:], origin='lower', cmap='gray')
                ax5.imshow(seg_array[:,y,:], origin='lower', cmap='jet', alpha=0.3)
                ax6.imshow(img2_array[:,:,z], origin='lower', cmap='gray')
                ax6.imshow(seg_array[:,:,z], origin='lower', cmap='jet', alpha=0.3)

                ax7.imshow(img1_array[x,:,:], cmap='gray')
                ax7.imshow(img2_array[x,:,:], cmap=colormap, alpha=0.3)
                ax7.imshow(seg_array[x,:,:], origin='lower', cmap='jet', alpha=0.3)

                ax8.imshow(img1_array[:,y,:], origin='lower', cmap='gray')
                ax8.imshow(img2_array[:,y,:], origin='lower', cmap=colormap, alpha=0.3)
                ax8.imshow(seg_array[:,y,:], origin='lower', cmap='jet', alpha=0.3)

                ax9.imshow(img1_array[:,:,z], origin='lower', cmap='gray')
                ax9.imshow(img2_array[:,:,z], origin='lower', cmap=colormap, alpha=0.3)
                ax9.imshow(seg_array[:,:,z], origin='lower', cmap='jet', alpha=0.3)

                ax1.set_xticks([])
                ax1.set_yticks([])
                ax2.set_xticks([])
                ax2.set_yticks([])
                ax3.set_xticks([])
                ax3.set_yticks([])
                ax4.set_xticks([])
                ax4.set_yticks([])
                ax5.set_xticks([])
                ax5.set_yticks([])
                ax6.set_xticks([])
                ax6.set_yticks([])
                ax7.set_xticks([])
                ax7.set_yticks([])
                ax8.set_xticks([])
                ax8.set_yticks([])
                ax9.set_xticks([])
                ax9.set_yticks([])

        if save_name is not None:
            plt.savefig(f"{save_name}", dpi=600)

        plt.show()


# add segmentation map functinality
