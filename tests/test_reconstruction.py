import numpy as np

from hipster import Reconstruction


def test_reconstruction():
    rg = Reconstruction("tests/models/vae_decoder.onnx")
    point = np.array([[1, 0, 0]], dtype=np.float32)
    assert rg(point).shape == (1, 1, 344)
