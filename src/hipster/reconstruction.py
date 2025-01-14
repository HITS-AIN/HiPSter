import os

import numpy as np
import onnxruntime as ort


class Reconstruction:

    def __init__(
        self,
        decoder_path: str | os.PathLike,
    ):
        self.decoder = ort.InferenceSession(os.fspath(decoder_path))

    def __call__(self, point: np.ndarray) -> np.ndarray:
        return self.decoder.run(None, {"l_x_": point})[0]
