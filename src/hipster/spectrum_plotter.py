import matplotlib.colors
import matplotlib.pyplot as plt
import numpy as np


class SpectrumPlotter:

    def __init__(
        self,
        wavelengths: np.ndarray,
        axis: bool = False,
        ylim: tuple | None = None,
        figsize_in_pixel: int = 800,
        dpi: int = 96,
        return_type: str = "ndarray",
    ):
        """Plot a spectrum with a spectral colormap in the background.

        Args:
            wavelengths (np.ndarray): Wavelengths of the spectrum.
            axis (bool, optional): Print axis labels. Defaults to False.
            ylim (tuple, optional): Y-axis limits. Defaults to (0.0, 1.0).
            figsize_in_pixel (int, optional): Size of the figure in pixels. Defaults to 800.
            dpi (int, optional): Dots per inch. Defaults to 96.
            return_type (str, optional): Type of return value ['plot', 'ndarray']. Defaults to "ndarray".
        """
        self.wavelengths = wavelengths
        self.axis = axis
        self.ylim = ylim
        self.figsize = figsize_in_pixel / dpi
        self.dpi = dpi
        self.return_type = return_type

        self.clim = (350, 780)
        norm = plt.Normalize(*self.clim)
        wl = np.arange(self.clim[0], self.clim[1] + 1, 2)
        colorlist = list(zip(norm(wl), [self.__wavelength_to_rgb(w) for w in wl]))
        self.spectralmap = matplotlib.colors.LinearSegmentedColormap.from_list(
            "spectrum", colorlist
        )

    def __call__(self, spectrum: np.ndarray):

        fig, ax = plt.subplots(figsize=(self.figsize, self.figsize), dpi=self.dpi)
        # fig = plt.figure(figsize=(self.figsize, self.figsize), dpi=self.dpi)
        # ax = fig.gca()
        # ax.axis("tight")

        ax.plot(self.wavelengths, spectrum, color="black")

        y = np.linspace(0, 6, 100)
        X, Y = np.meshgrid(self.wavelengths, y)

        extent = (
            np.min(self.wavelengths),
            np.max(self.wavelengths),
            np.min(y),
            np.max(y),
        )

        ax.imshow(
            X, clim=self.clim, extent=extent, cmap=self.spectralmap, aspect="auto"
        )

        if self.ylim:
            ax.set_ylim(self.ylim)

        if self.axis:
            ax.set_xlabel("Wavelength (nm)")
            ax.set_ylabel("Intensity")
        else:
            ax.axis("off")

        ax.fill_between(self.wavelengths, spectrum, 8, color="w")

        if self.return_type == "plot":
            return ax
        elif self.return_type == "ndarray":
            canvas = fig.canvas
            canvas.draw_idle()
            data = np.frombuffer(canvas.tostring_argb(), dtype="uint8")
            data = data.reshape(*reversed(canvas.get_width_height()), 4)[:, :, 1:4]
            return data
        else:
            raise RuntimeError("Invalid return type. Choose 'axes' or 'ndarray'.")

    def __wavelength_to_rgb(self, wavelength, gamma=0.8):
        """taken from http://www.noah.org/wiki/Wavelength_to_RGB_in_Python
        This converts a given wavelength of light to an
        approximate RGB color value. The wavelength must be given
        in nanometers in the range from 380 nm through 750 nm
        (789 THz through 400 THz).

        Based on code by Dan Bruton
        http://www.physics.sfasu.edu/astro/color/spectra.html
        Additionally alpha value set to 0.5 outside range
        """
        wavelength = float(wavelength)
        if wavelength >= 380 and wavelength <= 750:
            A = 1.0
        else:
            A = 0.5
        if wavelength < 380:
            wavelength = 380.0
        if wavelength > 750:
            wavelength = 750.0
        if wavelength >= 380 and wavelength <= 440:
            attenuation = 0.3 + 0.7 * (wavelength - 380) / (440 - 380)
            R = ((-(wavelength - 440) / (440 - 380)) * attenuation) ** gamma
            G = 0.0
            B = (1.0 * attenuation) ** gamma
        elif wavelength >= 440 and wavelength <= 490:
            R = 0.0
            G = ((wavelength - 440) / (490 - 440)) ** gamma
            B = 1.0
        elif wavelength >= 490 and wavelength <= 510:
            R = 0.0
            G = 1.0
            B = (-(wavelength - 510) / (510 - 490)) ** gamma
        elif wavelength >= 510 and wavelength <= 580:
            R = ((wavelength - 510) / (580 - 510)) ** gamma
            G = 1.0
            B = 0.0
        elif wavelength >= 580 and wavelength <= 645:
            R = 1.0
            G = (-(wavelength - 645) / (645 - 580)) ** gamma
            B = 0.0
        elif wavelength >= 645 and wavelength <= 750:
            attenuation = 0.3 + 0.7 * (750 - wavelength) / (750 - 645)
            R = (1.0 * attenuation) ** gamma
            G = 0.0
            B = 0.0
        else:
            R = 0.0
            G = 0.0
            B = 0.0
        return (R, G, B, A)
