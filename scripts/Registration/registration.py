import ants

class Registration:
    """

    """
    def __init__(self):

        self.fixed = None
        self.mytx = None

    def set_fixed_img(self, fixed: str):

        self.fixed = ants.image_read(fixed)

    def registation_trx(self, moving_pth=None):

        moving = ants.image_read(moving_pth)
        self.mytx = ants.registration(fixed=self.fixed, moving=moving, type_of_transform='Rigid')

    def transform(self, img, save_name=None):

        moving = ants.image_read(img)
        transformed_img = ants.apply_transforms(fixed=self.fixed, moving=moving, transformlist=self.mytx['fwdtransforms'])

        if save_name is not None:
            transformed_img.to_file(save_name)

        return transformed_img


