from hipster import generate_hips


def test_generate_hips():
    generate_hips("tests/models/vae_decoder.onnx", max_order=1, number_of_workers=1)
    assert True
