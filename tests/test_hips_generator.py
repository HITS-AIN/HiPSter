import numpy as np

from hipster import HiPSGenerator, Reconstruction, SpectrumPlotter


def test_hips_generator():

    hips_generator = HiPSGenerator(
        reconstruction=Reconstruction("tests/models/vae_decoder.onnx"),
        image_maker=SpectrumPlotter(np.arange(336, 1023, 2)),
    )

    hips_generator(max_order=1)
