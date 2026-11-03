# Usage

## HiPS and HEALPix

HiPSter uses the HEALPix framework to generate a Hierarchical Progressive Survey (HiPS) for the
corresponding spherical latent space positions. The HiPS representation can be visualized with
[Aladin Lite](https://github.com/cds-astro/aladin-lite).

```{figure} assets/HEALPix.png
---
name: fig:healpix
width: 500px
align: center
---
Source: {cite}`Fernique_2015`
```

## Command line interface

HiPSter is driven by a YAML configuration file:

```bash
hipster --config <path_to_config_file>
```

| Option | Description |
|---|---|
| `--config` | Path to the config file. |
| `--root_path` | Output directory for all tasks and the HTML page. Defaults to `./HiPSter`. |
| `--only_html` | Only (re)generate the HTML page, skip the tasks. |
| `--overwrite` | Allow writing into an existing `root_path`. |
| `-v`, `--verbose` | Print the base URL and the list of tasks. |
| `--version` | Print the version and exit. |

Every value of the config file can also be set or overridden on the command line, e.g.
`--html.title "My HiPS"`. Run `hipster --help` for the full list.

## Configuration file

A configuration file has three parts:

- `root_path`: the output directory, which is passed on to the HTML page and all tasks.
- `html`: settings for the generated Aladin Lite page (`url`, `title`, `aladin_lite_version`),
  see {class}`hipster.HTMLGenerator`.
- `tasks`: a list of tasks, each given by a `class_path` and its `init_args`. They are executed in
  order and each one adds an image layer or a catalog to the HTML page. Set `skip: true` to keep a
  task on the page without re-running it.

```yaml
root_path: HiPSter
html:
  url: http://localhost:8083
  title: HiPSter representation of Gaia XP DR3
  aladin_lite_version: latest
tasks:
  - class_path: hipster.HiPSGenerator
    init_args:
      decoder:
        model_path: decoder.onnx
      image_maker:
        class_path: hipster.SpectrumPlotter
        init_args:
          wavelengths:
            start: 336
            stop: 1021
            step: 2
          ylim: [0, 1]
          margin: 0.02
          figsize_in_pixel: 128
          flip: True
      hips_id: Gaia1
      hips_name: Gaia XP DR3 model spectrum
      hips_path: gaia/model_spectrum
      max_order: 2
      hierarchy: 2
  - class_path: hipster.VOTableGenerator
    init_args:
      encoder:
        model_path: encoder.onnx
      data_directory: data/gaia/xp_calibrated
      color: red
      shape: circle
      size: 10
```

More complete configurations are in the
[`examples/`](https://github.com/HITS-AIN/HiPSter/tree/main/examples) directory.

### Tasks

| Class | Purpose |
|---|---|
| {class}`~hipster.HiPSGenerator` | Decodes the HEALPix cell centers with the model's decoder and renders the reconstructions as HiPS tiles. |
| {class}`~hipster.DatasetProjection` | Encodes a dataset with the model's encoder and places the real images at their latent space positions as HiPS tiles. |
| {class}`~hipster.VOTableGenerator` | Encodes a dataset and writes a VOTable catalog with the latent space positions, shown as an overlay in Aladin Lite. |
| {class}`~hipster.NumberedHiPSGenerator` | Labels each HiPS tile with its order and pixel number, useful to check the tiling. No model required. |

`max_order` sets the deepest HiPS order to generate and `hierarchy` the number of sub-cells per tile
edge. `distortion_correction` compensates the distortion of the HEALPix cells.

### Image makers

The `image_maker` of a task turns the model output into a tile image.

| Class | Purpose |
|---|---|
| {class}`~hipster.ImagePlotter` | 2D images, e.g. galaxy images. |
| {class}`~hipster.SpectrumPlotter` | Spectra plotted over a spectral color map. The wavelengths are given as a {class}`~hipster.Range`. |
| {class}`~hipster.AbsorptionLinePlotter` | Spectra plotted as absorption lines. |

### Models

Encoders and decoders are ONNX models, e.g. exported from Spherinator, loaded with
{class}`hipster.Inference`. Set `model_path`, and `input_name` if the model input is not called
`x`:

```yaml
decoder:
  model_path: decoder.onnx
  input_name: z
```

## Visualization

HiPSter writes an `index.html` into `root_path` that loads all HiPS layers and catalogs from
`html.url`. Serve `root_path` at that URL with any static web server, for example:

```bash
cd <root_path>
python3 -m http.server 8083
```

and open <http://localhost:8083> in a browser. In a clone of the repository, `src/server.py`
starts the same server on port 8083 with CORS headers enabled.

See the {doc}`API reference <api>` for all classes and their parameters.
