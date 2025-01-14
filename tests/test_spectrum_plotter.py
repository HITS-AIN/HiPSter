import numpy as np

from hipster import SpectrumPlotter


def test_reconstruction():
    wavelengths = np.arange(200, 1000, 1000)
    spectrum = (5 + np.sin(wavelengths * 0.1) ** 2) * np.exp(
        -0.00002 * (wavelengths - 600) ** 2
    )
    spectrum_plotter = SpectrumPlotter(wavelengths)
    assert spectrum_plotter(spectrum) is not None
