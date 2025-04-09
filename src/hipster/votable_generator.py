import math
import os

import healpy
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.dataset as ds
from astropy.io.votable import writeto
from astropy.table import Table

from hipster.html_generator import HTMLGenerator

from .inference import Inference
from .task import Task


class VOTableGenerator(Task):

    def __init__(
        self,
        encoder: Inference,
        data_directory: str,
        output_file: str = "votable.vot",
        url: str = "http://localhost:8083",
        batch_size: int = 256,
        catalog_name: str = "",
        color: str = "red",
        shape: str = "circle",
        size: int = 10,
        **kwargs,
    ):
        """Generates a catalog of data.

        Args:
            encoder (callable): Function that encodes the data.
            data_directory (str): The directory containing the data.
            output_file (str, optional): The output file name. Defaults to "votable.xml".
            url (str): The URL of the HiPS server. Defaults to "http://localhost:8083".
            batch_size (int, optional): The batch size to use. Defaults to 256.
            catalog_name (str, optional): The name of the catalog. Defaults to "".
            color (str, optional): The color of the catalog. Defaults to "red".
            shape (str, optional): The shape of the catalog. Defaults to "circle".
            size (int, optional): The size of the catalog. Defaults to 10.
            **kwargs: Additional keyword arguments.
        """
        super().__init__("VOTableGenerator", **kwargs)
        self.encoder = encoder
        self.data_directory = data_directory
        self.output_file = output_file
        self.url = url
        self.batch_size = batch_size
        self.catalog_name = catalog_name
        self.color = color
        self.shape = shape
        self.size = size

    def get_data(self) -> pd.DataFrame:
        """Generates the catalog."""

        data = {
            "preview": [],
            "source_id": [],
            "latent_position": [],
            "RA2000": [],
            "DEC2000": [],
        }
        dataset = ds.dataset(self.data_directory, format="parquet")
        # dataset = dataset.filter(ds.field("source_id") % 10 == 0)

        # Reshape the data if the shape is stored in the metadata.
        metadata_shape = b"flux_shape"
        if dataset.schema.metadata and metadata_shape in dataset.schema.metadata:
            shape_string = dataset.schema.metadata[metadata_shape].decode("utf8")
            shape = shape_string.replace("(", "").replace(")", "").split(",")
            shape = tuple(map(int, shape))

        for batch in dataset.to_batches(batch_size=self.batch_size):
            flux = batch["flux"].flatten().to_numpy().reshape(-1, *shape)

            # if flux.shape[0] != self.batch_size:
            #     print(f"Skipping batch with shape {flux.shape}")
            #     continue

            # Normalize the flux.
            # flux is read-only, so we need to create a copy.
            flux = flux.copy()
            for i, x in enumerate(flux):
                flux[i] = (x - x.min()) / (x.max() - x.min())

            latent_position = self.encoder(flux)

            angles = np.array(healpy.vec2ang(latent_position)) * 180.0 / math.pi
            angles = angles.T

            for source_id in batch["source_id"]:
                data["preview"].append(
                    "<a href='"
                    + self.url
                    + "/"
                    + self.title
                    + "/images/"
                    + str(source_id)
                    + ".jpg' target='_blank'>"
                    "<img src='"
                    + self.url
                    + "/"
                    + self.title
                    + "/thumbnails/"
                    + str(source_id)
                    + ".jpg'></a>,"
                )
            data["source_id"].extend(batch["source_id"].to_pylist())
            data["latent_position"].extend(latent_position)
            data["RA2000"].extend(angles[:, 1])
            data["DEC2000"].extend(90.0 - angles[:, 0])

        return pa.table(data).to_pandas()

    def execute(self) -> None:
        print(f"Executing task: {self.name}")
        table = Table.from_pandas(self.get_data())
        writeto(table, os.path.join(self.root_path, self.output_file))

    def register(self, html_generator: HTMLGenerator) -> None:
        """Register the VOTable to the HTML generator."""
        html_generator.add_votable(
            html_generator.VOTable(
                url=f"{html_generator.url}/{self.title}",
                name=self.catalog_name,
                color=self.color,
                shape=self.shape,
                size=self.size,
            )
        )
