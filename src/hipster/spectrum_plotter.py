import matplotlib.colors
import matplotlib.pyplot as plt
import numpy as np


class SpectrumPlotter:

    def __init__(
        self,
        wavelengths: np.ndarray,
        axis: bool = False,
        ylim: tuple | None = None,
    ):
        """_summary_

        Args:
            wavelengths (np.ndarray): Wavelengths of the spectrum.
            axis (bool, optional): Print axis labels. Defaults to False.
            ylim (tuple, optional): Y-axis limits. Defaults to (0.0, 1.0).
        """
        self.wavelengths = wavelengths
        self.axis = axis
        self.ylim = ylim
        self.clim = (350, 780)
        norm = plt.Normalize(*self.clim)
        wl = np.arange(self.clim[0], self.clim[1] + 1, 2)
        colorlist = list(zip(norm(wl), [self.__wavelength_to_rgb(w) for w in wl]))
        self.spectralmap = matplotlib.colors.LinearSegmentedColormap.from_list(
            "spectrum", colorlist
        )

    def __call__(self, spectrum: np.ndarray) -> plt.Axes:

        _, ax = plt.subplots(figsize=(4, 4))
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
        return ax

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
