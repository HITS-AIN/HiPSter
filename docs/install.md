# Installation

## For users

Install the published package, [`astro-hipster`](https://pypi.org/project/astro-hipster/), from PyPI.

### Using pip

We recommend installing into a virtual environment rather than system-wide:

```bash
python3 -m venv .venv
source .venv/bin/activate

pip install astro-hipster
```

### Using uv

If you have [uv](https://docs.astral.sh/uv/) installed, it manages the virtual environment for you:

```bash
uv venv
source .venv/bin/activate

uv pip install astro-hipster
```

### GPU support

Model inference runs on [ONNX Runtime](https://onnxruntime.ai/). To run it on an NVIDIA GPU, install
the `cuda` extra:

```bash
pip install "astro-hipster[cuda]"
```

### Verify the installation

```bash
hipster --version
hipster --help
```

This should print the installed version and the command-line usage. You're now ready to follow the
{doc}`usage guide <usage>` to generate your first HiPS tiling.

## For developers

Follow this path if you want to contribute to HiPSter, fix a bug, add a new task or image maker, or
run the test suite locally.

### Clone the repository

```bash
git clone https://github.com/HITS-AIN/HiPSter.git
cd HiPSter
```

### Set up the development environment

uv reads `pyproject.toml` and creates an isolated virtual environment with the exact locked
dependency versions from `uv.lock`:

```bash
uv sync --extra dev
```

This installs HiPSter itself in editable mode plus the `dev` extras (`pytest`, `ruff`, `pre-commit`,
...), so any change you make to the source under `src/hipster/` is picked up immediately.

You don't need to manually activate the virtual environment — prefix commands with `uv run` and uv
takes care of it. If you prefer an activated shell:

```bash
source .venv/bin/activate
```

Install the git hooks so that linting and formatting run on every commit:

```bash
uv run pre-commit install
```

### Run the test suite

```bash
uv run --extra dev pytest
```

Run a single test file or test:

```bash
uv run --extra dev pytest tests/test_hips_generator.py
uv run --extra dev pytest tests/test_hips_generator.py::test_hips_generator_image
```

### Lint and format

HiPSter uses [ruff](https://docs.astral.sh/ruff/) for both linting and formatting.

```bash
uv run --extra dev ruff check --no-fix
uv run --extra dev ruff format --check
```

Run these before opening a pull request.

### Run HiPSter locally

Once the environment is set up, the `hipster` CLI is available via `uv run`. The numbering example
needs no trained model and is a quick way to check that everything works:

```bash
uv run hipster --config examples/numbering.yaml
```

See the {doc}`usage guide <usage>` for details on writing configuration files and viewing the result.

### Build the documentation

The documentation (this site) is built with [Sphinx](https://www.sphinx-doc.org/) from the `docs/`
directory using the `docs` extra:

```bash
uv sync --extra docs
uv run --extra docs sphinx-build -b html docs docs/_build/html
```

Open `docs/_build/html/index.html` in a browser to preview it. For live-reloading while editing:

```bash
uv run --extra docs sphinx-autobuild docs docs/_build/html
```
