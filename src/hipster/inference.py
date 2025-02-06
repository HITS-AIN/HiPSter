import os

import numpy as np
import onnxruntime as ort


class Inference:

    def __init__(
        self,
        model_path: str | os.PathLike,
    ):
        self.model = ort.InferenceSession(os.fspath(model_path))

    def __call__(self, data: np.ndarray) -> np.ndarray:
        return self.model.run(None, {"l_x_": data})[0]
