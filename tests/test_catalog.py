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

    assert "x" in catalog

    print(catalog["x"][0])
    assert np.allclose(catalog["x"][0], -0.14086828)
