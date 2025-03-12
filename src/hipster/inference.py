import os

import numpy as np
import onnxruntime as ort


class Inference:

    def __init__(
        self,
        model_path: str | os.PathLike,
        batch_size: int = 256,
    ):
        self.model = ort.InferenceSession(os.fspath(model_path))
        self.batch_size = batch_size

    def __call__(self, data: np.ndarray) -> np.ndarray:
        results = []
        for i in range(0, len(data), self.batch_size):
            batch = data[i : i + self.batch_size]
            results.append(self.model.run(None, {"l_x_": batch})[0])
        data = np.concatenate(results, axis=0)
        return data
