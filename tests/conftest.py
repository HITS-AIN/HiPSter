import random

import numpy as np
import pytest
import torch


@pytest.hookimpl
def pytest_runtest_setup():
    """Seed all random number generators to be fully deterministic."""
    np.random.seed(0)
    random.seed(0)
    torch.manual_seed(0)
    # torch.use_deterministic_algorithms(True)
