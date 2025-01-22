import numpy as np

from hipster import Inference


def test_inference_decoder():
    rg = Inference("tests/models/vae_decoder.onnx")
    point = np.array([[1, 0, 0]], dtype=np.float32)
    assert rg(point).shape == (1, 1, 344)
