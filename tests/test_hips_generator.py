import numpy as np
import pytest

from hipster import HiPSGenerator, Inference, SpectrumPlotter


@pytest.mark.parametrize("hierarchy", [1, 2])
def test_hips_generator(tmp_path, hierarchy):

    hips_generator = HiPSGenerator(
        decoder=Inference("tests/models/vae_decoder.onnx"),
        image_maker=SpectrumPlotter(
            np.arange(336, 1023, 2),
            ylim=(0, 1),
            figsize_in_pixel=64,
        ),
        output_folder=tmp_path,
        hierarchy=hierarchy,
    )

    hips_generator(max_order=1)
