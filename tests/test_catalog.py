import numpy as np

from hipster import Inference, VOTableGenerator


def test_catalog_generator():

    votable_generator = VOTableGenerator(
        encoder=Inference("tests/models/vae_encoder.onnx", input_name="l_x_"),
        data_directory="tests/data/XpSampledMeanSpectrum",
        dataset="gaia",
        data_column="flux",
    )

    catalog = votable_generator.get_catalog()

    assert np.allclose(catalog["x"][0], -0.1408, atol=1e-3)
    assert np.allclose(catalog["y"][0], 0.0060, atol=1e-3)
    assert np.allclose(catalog["z"][0], 0.9900, atol=1e-3)
