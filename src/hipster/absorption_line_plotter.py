import matplotlib
import matplotlib.pyplot as plt
import numpy as np

from .wavelength_to_rgb import wavelength_to_rgb

matplotlib.use("Agg")


class AbsorptionLinePlotter:

    def __init__(
        self,
        wavelengths: np.ndarray,
        normalize: bool = True,
        figsize_in_pixel: int = 800,
        dpi: int = 96,
    ):
        """Plot a spectrum with a spectral colormap in the background.

        Args:
            wavelengths (np.ndarray): Wavelengths of the spectrum.
            normalize (bool, optional): Normalize the spectrum. Defaults to True.
            figsize_in_pixel (int, optional): Size of the figure in pixels. Defaults to 800.
            dpi (int, optional): Dots per inch. Defaults to 96.
        """
        self.wavelengths = wavelengths
        self.normalize = normalize
        self.figsize = figsize_in_pixel / dpi
        self.dpi = dpi

    def __call__(self, flux: np.ndarray) -> np.ndarray:

        if self.normalize:
            flux = (flux - np.min(flux)) / (np.max(flux) - np.min(flux))

        height = 100  # how "tall" you want the 2D image
        n_wl = len(self.wavelengths)
        # Initialize (height, n_wl, 3) for an RGB image
        spectrum_image_rgb = np.zeros((height, n_wl, 3))
        for i, wl in enumerate(self.wavelengths):
            base_color = wavelength_to_rgb(wl, gamma=0.8)
            # Scale the color by flux to adjust brightness
            # You could adjust scaling or normalization here if needed.
            color_col = [c * flux[i] for c in base_color]

            # Fill this column (all rows in column i have the same color)
            spectrum_image_rgb[:, i, :] = color_col

        fig, ax = plt.subplots(figsize=(self.figsize, self.figsize), dpi=self.dpi)
        fig.tight_layout()

        ax.imshow(spectrum_image_rgb, origin="lower", aspect="auto")
        ax.axis("off")

        plt.subplots_adjust(0, 0, 1, 1, 0, 0)

        canvas = fig.canvas
        canvas.draw_idle()
        data = np.frombuffer(canvas.tostring_argb(), dtype="uint8")
        data = data.reshape(*reversed(canvas.get_width_height()), 4)[:, :, 1:4]

        plt.close(fig)
        return data
