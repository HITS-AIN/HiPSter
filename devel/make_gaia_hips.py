#!/usr/bin/env python

import argparse
import sys

import numpy as np

from hipster import HiPSGenerator, Reconstruction, SpectrumPlotter


def main() -> int:

    parser = argparse.ArgumentParser(description="Generate HiPS from a model.")
    parser.add_argument(
        "--decoder",
        "-d",
        default="decoder.onnx",
        help="ONNX file of the trained decoder model.",
    )
    parser.add_argument(
        "--output_folder",
        default="./HiPSter",
        help="Output of HiPS (default = './HiPSter').",
    )
    parser.add_argument(
        "--max_order",
        "-m",
        default=4,
        type=int,
        help="Maximal order of HiPS tiles (default = 4).",
    )
    parser.add_argument(
        "--hierarchy",
        default=1,
        type=int,
        help="Number of tiles hierarchically combined (default = 1).",
    )
    parser.add_argument(
        "--size",
        "-s",
        default=64,
        type=int,
        help="Image output size (default = 64).",
    )
    args = parser.parse_args()

    hips_generator = HiPSGenerator(
        reconstruction=Reconstruction(args.decoder),
        image_maker=SpectrumPlotter(
            np.arange(336, 1023, 2), ylim=(0, 1), figsize_in_pixel=args.size
        ),
        output_folder=args.output_folder,
        hierarchy=args.hierarchy,
    )

    hips_generator(max_order=args.max_order)


if __name__ == "__main__":
    sys.exit(main())
