import matplotlib
import matplotlib.pyplot as plt
import numpy as np

from .range import Range
from .wavelength_to_rgb import wavelength_to_rgb

matplotlib.use("Agg")


class ImagePlotter:

    def __init__(
        self,
        flip: bool = False,
    ):
        """Plot a 2D image

        Args:
            flip (bool, optional): Flip the image. Defaults to False.
        """
        self.figsize_in_pixel = None
        self.flip = flip

    def __call__(self, data: np.ndarray) -> np.ndarray:

        # Store the size of the image for the HiPS property file
        self.figsize_in_pixel = data.shape[1]

        data = np.clip(data.transpose(1, 2, 0), 0, 1) * 255

        if self.flip:
            data = np.fliplr(data)

        return data
