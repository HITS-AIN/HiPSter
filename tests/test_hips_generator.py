import pytest

from hipster import HiPSGenerator, Inference, Range, SpectrumPlotter


@pytest.mark.parametrize("hierarchy", [1, 2])
def test_hips_generator(tmp_path, hierarchy):

    hips_generator = HiPSGenerator(
        decoder=Inference("tests/models/vae_decoder.onnx", input_name="l_x_"),
        image_maker=SpectrumPlotter(
            Range(336, 1023, 2),
            ylim=(0, 1),
            figsize_in_pixel=64,
        ),
        output_folder=tmp_path,
        hierarchy=hierarchy,
    )

    hips_generator(max_order=1)
