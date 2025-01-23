from hipster import CatalogGenerator, Inference


def test_hips_generator():

    catalog_generator = CatalogGenerator(
        encoder=Inference("tests/models/vae_encoder.onnx"),
        data_directory="tests/data",
    )

    catalog_generator()
