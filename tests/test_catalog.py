from hipster import CatalogGenerator, Inference


def test_catalog_generator():

    catalog_generator = CatalogGenerator(
        encoder=Inference("tests/models/vae_encoder.onnx"),
        data_directory="tests/data/XpSampledMeanSpectrum",
    )

    catalog = catalog_generator()

    assert "source_id" in catalog
    assert "latent_position" in catalog
