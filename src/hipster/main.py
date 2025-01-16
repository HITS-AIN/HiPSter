#!/usr/bin/env python3

import argparse
import sys

import yaml

from hipster import HiPSGenerator, Reconstruction, SpectrumPlotter


def main() -> int:
    list_of_tasks = [
        "hips",
        "catalog",
        "votable",
        "projection",
        "images",
        "thumbnails",
        "allsky",
        "all",
    ]

    parser = argparse.ArgumentParser(
        description="Transform a model in a HiPS representation"
    )
    parser.add_argument(
        "--task",
        "-t",
        nargs="+",
        default=["all"],
        help="Execution task [" + ", ".join(list_of_tasks) + "].",
    )
    parser.add_argument(
        "--config",
        "-c",
        default="config.yaml",
        help="config file (default = 'config.yaml').",
    )
    parser.add_argument(
        "--checkpoint",
        "-m",
        default="model.ckpt",
        help="checkpoint file (default = 'model.ckpt').",
    )
    parser.add_argument(
        "--max_order",
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
        "--crop_size", default=256, type=int, help="Image crop size (default = 256)."
    )
    parser.add_argument(
        "--output_size", default=64, type=int, help="Image output size (default = 64)."
    )
    parser.add_argument(
        "--output_folder",
        default="./HiPSter",
        help="Output of HiPS (default = './HiPSter').",
    )
    parser.add_argument(
        "--title", default="Illustris", help="HiPS title (default = 'Illustris')."
    )
    parser.add_argument(
        "--distortion", action="store_true", help="Enable distortion correction."
    )
    parser.add_argument(
        "--verbose", "-v", default=0, action="count", help="Print level."
    )

    args = parser.parse_args()

    # Check if the tasks are valid
    if not set(args.task) <= set(list_of_tasks):
        raise ValueError(f"Task '{args.task}' not in list of tasks: {list_of_tasks}")

    # If "all" is in the list of tasks, replace it with all tasks except "all"
    if "all" in args.task:
        args.task = list_of_tasks[:-1]

    print(f"Executing task(s): {', '.join(args.task)}")

    with open(args.config, "r", encoding="utf-8") as stream:
        config = yaml.load(stream, Loader=yaml.Loader)

    hipster = Hipster(
        args.output_folder,
        args.title,
        max_order=args.max_order,
        hierarchy=args.hierarchy,
        crop_size=args.crop_size,
        output_size=args.output_size,
        distortion_correction=args.distortion,
        catalog_file="catalog.csv",
        votable_file="catalog.vot",
        verbose=args.verbose,
    )

    if "hips" in args.task:
        hipster.generate_hips(model)

    if "catalog" in args.task:
        hipster.generate_catalog(model, datamodule)

    if "votable" in args.task:
        hipster.transform_csv_to_votable()

    if "projection" in args.task:
        hipster.generate_dataset_projection(datamodule)

    if "images" in args.task:
        hipster.create_images(datamodule)

    if "thumbnails" in args.task:
        hipster.create_thumbnails(datamodule)

    if "allsky" in args.task:
        hipster.create_allsky()

    return 0


if __name__ == "__main__":
    sys.exit(main())
