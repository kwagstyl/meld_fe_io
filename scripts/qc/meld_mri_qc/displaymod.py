import os
import SimpleITK as sitk
import numpy as np
import matplotlib.pyplot as plt
import warnings


class DisplayModalities:

    def __init__(self):
        pass

    @staticmethod
    def path_validator(path: str):

        if not os.path.exists(path):
            raise NotADirectoryError(f"Provided img path {path} does not exist, please enter valid path.")

    @staticmethod
    def coords_extract(array: np.array) -> tuple:

        return int(array.shape[0]/2), int(array.shape[1]/2), int(array.shape[2]/2)


    @staticmethod
    def coords_seg_extract(seg_array: np.array) -> tuple:
        
        x_coord = None
        x_size = 0
        y_coord = None
        y_size = 0
        z_coord = None
        z_size = 0

        for i in range(0, seg_array.shape[0]):
            if len(seg_array[i,:,:,1].nonzero()[0]) > x_size:
                x_coord = i
                x_size = len(seg_array[i,:,:,1].nonzero()[0])

        for i in range(0, seg_array.shape[1]):
            if len(seg_array[:,i,:,1].nonzero()[0]) > y_size:
                y_coord = i
                y_size = len(seg_array[:,i,:,1].nonzero()[0])

        for i in range(0, seg_array.shape[2]):
            if len(seg_array[:,:,i,1].nonzero()[0]) > z_size:
                z_coord = i
                z_size = len(seg_array[:,:,i,1].nonzero()[0])

        return x_coord, y_coord, z_coord

    
    def display_image_sag_coron(self, img1, y=None, z=None, save_name=None): #'jet'

        self.path_validator(img1)

        img1_array = sitk.GetArrayFromImage(sitk.ReadImage(img1, sitk.sitkFloat32))  # convert to sitk object

        fig, axes = plt.subplots(1, 8, figsize=(12, 3))
        
        #add sagital
        if z is None:
            _, _, z = img1_array.shape
            z = int(z/2)
        z_values = [-20, -10, 10, 20]

        for ax, i in zip(axes[0:4], z_values):
            ax.imshow(img1_array[:,:,z+i], origin='lower', cmap='gray')
            ax.set_xticks([])
            ax.set_yticks([])
            
        #add coronal
        if y is None:
            _, y, _ = img1_array.shape
            y = int(y/2)

        y_values = [-20, -10, 10, 20]

        for ax, i in zip(axes[4::], y_values):
            ax.imshow(img1_array[:,y+i,:], origin='lower', cmap='gray')
            ax.set_xticks([])
            ax.set_yticks([])

        if save_name is not None:
            fig.patch.set_facecolor('black')
            fig.tight_layout()
            fig.subplots_adjust(wspace=0.0)
            plt.savefig(f"{save_name}", dpi=600)
        plt.close()
        
        
    def display_overlay_sag_coron(self, t1, post_op, seg, y=None, z=None, save_name=None): #'jet'


        self.path_validator(t1)

        t1_array = sitk.GetArrayFromImage(sitk.ReadImage(t1, sitk.sitkFloat32))  # convert to sitk object
        postop_array = sitk.GetArrayFromImage(sitk.ReadImage(post_op, sitk.sitkFloat32)) if post_op is not None else None
        seg_array = sitk.GetArrayFromImage(sitk.LabelToRGB(sitk.ReadImage(seg, sitk.sitkInt64)))
        
        if t1_array.shape[0:3] != seg_array.shape[0:3]:
            warnings.warn(f"CAUTION: There is a LABEL array size mismatch between the MR volume (1), {t1}, and {seg}."
                        f"This may affect acuracy of overlapped visualisation.")

        fig, axes = plt.subplots(4, 6, figsize=(12, 10)) if post_op is not None else plt.subplots(2, 6, figsize=(12, 5))
        arrays = [t1_array, t1_array, postop_array, postop_array] if post_op is not None else [t1_array, t1_array]
        
        #add sagital
        if z is None:
            coords = self.coords_seg_extract(seg_array)
            z = coords[2]

        z_values = [-3, 0, 3]

        for i, ax_row in enumerate(axes):
            for j, ax in enumerate(ax_row[0:3]):
                z_val = z_values[j]
                array = arrays[i]
                ax.imshow(array[:,:,z+z_val], origin='lower', cmap='gray')
                if (i+1) % 2 == 0:
                    ax.imshow(seg_array[:,:,z+z_val], origin='lower', cmap='jet', alpha=0.3)
                ax.set_xticks([])
                ax.set_yticks([])

        #add coronal

        if y is None:
            coords = self.coords_seg_extract(seg_array)
            y = coords[1]

        y_values = [-3, 0, 3]

        for i, ax_row in enumerate(axes):
            for j, ax in enumerate(ax_row[3::]):
                y_val = y_values[j]
                array = arrays[i]
                ax.imshow(array[:,y+y_val,:], origin='lower', cmap='gray')
                if (i+1) % 2 == 0:
                    ax.imshow(seg_array[:,y+y_val,:], origin='lower', cmap='jet', alpha=0.3)
                ax.set_xticks([])
                ax.set_yticks([])

        if save_name is not None:
            fig.patch.set_facecolor('black')
            plt.tight_layout()
            fig.subplots_adjust(wspace=0)
            plt.savefig(f"{save_name}", dpi=600)
        plt.close()





