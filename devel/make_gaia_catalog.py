#!/usr/bin/env python

import argparse
import sys

from astropy.io.votable import writeto
from astropy.table import Table

from hipster import CatalogGenerator, Inference


def main() -> int:

    parser = argparse.ArgumentParser(description="Generate catalog.")
    parser.add_argument(
        "--encoder",
        "-e",
        default="encoder.onnx",
        help="ONNX file of the trained encoder model.",
    )
    parser.add_argument(
        "--data_directory",
        help="Data directory with parquet files.",
    )
    parser.add_argument(
        "--output_folder",
        default="./HiPSter",
        help="Output of HiPS (default = './HiPSter').",
    )
    args = parser.parse_args()

    catalog_generator = CatalogGenerator(
        encoder=Inference(args.encoder),
        data_directory=args.data_directory,
    )

    catalog = catalog_generator()
    table = Table.from_pandas(catalog)
    writeto(table, "catalog.vot")

    return 0


if __name__ == "__main__":
    sys.exit(main())
