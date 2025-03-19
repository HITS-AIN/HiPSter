#!/usr/bin/env python

import sys

from hipster import (
    AbsorptionLinePlotter,
    HiPSGenerator,
    ImageGenerator,
    Inference,
    Range,
    SpectrumPlotter,
    VOTableGenerator,
)


def main() -> int:

    tasks = [
        # "spectrum",
        # "absorption_line",
        "votable",
        # "images",
        # "thumbnails",
    ]
    url = "http://localhost:8083"
    title = "gaia"
    encoder = "/home/doserbd/git/Spherinator/gaia/gaia-calibrated-v1/encoder.onnx"
    decoder = "/home/doserbd/git/Spherinator/gaia/gaia-calibrated-v1/decoder.onnx"
    data_directory = "/home/doserbd/data/gaia/xp_calibrated/parquet_subset"
    output_folder = "./HiPSter/" + title
    hips_tile_size = 128
    hierarchy = 4
    max_order = 4

    if "spectrum" in tasks:
        spectrum_plotter = SpectrumPlotter(
            Range(336, 1021, 2),
            ylim=(0, 1),
            figsize_in_pixel=hips_tile_size,
            margin=0.02,
            flip=True,
        )
        hips_generator = HiPSGenerator(
            decoder=Inference(decoder),
            image_maker=spectrum_plotter,
            output_folder=output_folder + "/model_spectrum",
            hierarchy=hierarchy,
            max_order=max_order,
        )
        hips_generator.execute()

    if "absorption_line" in tasks:
        absorption_line_plotter = AbsorptionLinePlotter(
            Range(336, 1021, 2),
            figsize_in_pixel=hips_tile_size,
            margin=0.02,
            flip=True,
        )
        hips_generator = HiPSGenerator(
            decoder=Inference(decoder),
            image_maker=absorption_line_plotter,
            output_folder=output_folder + "/model_absorption_line",
            hierarchy=hierarchy,
            max_order=max_order,
        )
        hips_generator.execute()

    if "votable" in tasks:
        VOTableGenerator(
            encoder=Inference(encoder),
            data_directory=data_directory,
            output_file=output_folder + "/catalog.vot",
            url=url,
            title=title,
        ).execute()

    if "images" in tasks:
        ImageGenerator(
            encoder=Inference(encoder),
            decoder=Inference(decoder),
            data_directory=data_directory,
            output_folder=output_folder + "/images",
        )()

    if "thumbnails" in tasks:
        ImageGenerator(
            encoder=Inference(encoder),
            decoder=Inference(decoder),
            data_directory=data_directory,
            output_folder=output_folder + "/thumbnails",
            figsize_in_pixel=(120, 90),
            legend=False,
        )()

    return 0


if __name__ == "__main__":
    sys.exit(main())
