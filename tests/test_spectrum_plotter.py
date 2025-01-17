import numpy as np

from hipster import SpectrumPlotter


def test_spectrum_plotter():
    wavelengths = np.arange(200, 1000, 1000)
    spectrum = (5 + np.sin(wavelengths * 0.1) ** 2) * np.exp(
        -0.00002 * (wavelengths - 600) ** 2
    )
    spectrum_plotter = SpectrumPlotter(wavelengths, return_type="plot")
    spectrum = spectrum_plotter(spectrum)
    assert spectrum is not None


def test_spectrum_plotter_ndarray():
    wavelengths = np.arange(200, 1000, 1000)
    spectrum = (5 + np.sin(wavelengths * 0.1) ** 2) * np.exp(
        -0.00002 * (wavelengths - 600) ** 2
    )
    spectrum_plotter = SpectrumPlotter(wavelengths, return_type="ndarray")
    spectrum = spectrum_plotter(spectrum)
    assert spectrum is not None
