import numpy as np

from hipster import Inference, VOTableGenerator


def test_catalog_generator():

    votable_generator = VOTableGenerator(
        encoder=Inference("tests/models/vae_encoder.onnx", input_name="l_x_"),
        data_directory="tests/data/XpSampledMeanSpectrum",
        data_column="flux",
    )

    catalog = votable_generator.get_catalog()

    assert "source_id" in catalog
    assert "latent_position" in catalog

    print(catalog["latent_position"][0])
    assert np.allclose(
        catalog["latent_position"][0], [-0.14086828, 0.00598068, 0.9900103]
    )
