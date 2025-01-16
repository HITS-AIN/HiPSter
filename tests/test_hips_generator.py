import numpy as np

from hipster import HiPSGenerator, Reconstruction, SpectrumPlotter


def test_hips_generator(tmp_path):

    hips_generator = HiPSGenerator(
        reconstruction=Reconstruction("tests/models/vae_decoder.onnx"),
        image_maker=SpectrumPlotter(
            np.arange(336, 1023, 2), ylim=(0, 1), figsize_in_pixel=400
        ),
        output_folder=tmp_path,
    )

    hips_generator(max_order=1)


def test_hips_generator_2(tmp_path):

    hips_generator = HiPSGenerator(
        reconstruction=Reconstruction("tests/models/vae_decoder.onnx"),
        image_maker=SpectrumPlotter(
            np.arange(336, 1023, 2),
            ylim=(0, 1),
            figsize_in_pixel=64,
        ),
        output_folder=tmp_path,
        hierarchy=2,
    )

    hips_generator(max_order=1)
