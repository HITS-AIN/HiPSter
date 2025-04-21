from hipster import Inference, VOTableGenerator


def test_catalog_generator():

    votable_generator = VOTableGenerator(
        encoder=Inference("tests/models/vae_encoder.onnx", input_name="l_x_"),
        data_directory="tests/data/XpSampledMeanSpectrum",
        data_column="flux",
    )

    catalog = votable_generator.get_data()

    assert "source_id" in catalog
    assert "latent_position" in catalog
