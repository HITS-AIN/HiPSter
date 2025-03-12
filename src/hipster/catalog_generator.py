import math

import healpy
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.dataset as ds

from .inference import Inference


class CatalogGenerator:

    def __init__(
        self,
        encoder: Inference,
        data_directory: str,
        url: str = "http://localhost:8083",
        title: str = "title",
        batch_size: int = 256,
    ):
        """Generates a catalog of data.

        Args:
            encoder (callable): Function that encodes the data.
            data_directory (str): The directory containing the data.
            url (str): The URL of the HiPS server. Defaults to "http://localhost:8083".
            title (str): The title of the HiPS. Defaults to "title".
            batch_size (int, optional): The batch size to use. Defaults to 256.
        """

        self.encoder = encoder
        self.data_directory = data_directory
        self.url = url
        self.title = title
        self.batch_size = batch_size

    def __call__(self) -> pd.DataFrame:

        data = {
            "preview": [],
            "source_id": [],
            "latent_position": [],
            "RA2000": [],
            "DEC2000": [],
        }
        dataset = ds.dataset(self.data_directory, format="parquet")

        # Reshape the data if the shape is stored in the metadata.
        metadata_shape = b"flux_shape"
        if dataset.schema.metadata and metadata_shape in dataset.schema.metadata:
            shape_string = dataset.schema.metadata[metadata_shape].decode("utf8")
            shape = shape_string.replace("(", "").replace(")", "").split(",")
            shape = tuple(map(int, shape))

        for batch in dataset.to_batches(batch_size=self.batch_size):
            flux = batch["flux"].flatten().to_numpy().reshape(-1, *shape)

            if flux.shape[0] != self.batch_size:
                print(f"Skipping batch with shape {flux.shape}")
                continue

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

        table = pa.table(data)
        return table.to_pandas()

    #     with open(self.catalog_file, "w", encoding="utf-8") as output:
    #         output.write(
    #             "#preview,simulation,snapshot data,subhalo id,subhalo data,RMSE,id,RA2000,DEC2000,rotation,x,y,z\n"
    #         )

    #         for batch, metadata in tqdm(self.dataloader_processing):
    #             _, rotations, coordinates, losses = model.find_best_rotation(batch)

    #             rotations = rotations.cpu().detach().numpy()
    #             coordinates = coordinates.cpu().detach().numpy()
    #             losses = losses.cpu().detach().numpy()
    #             angles = numpy.array(healpy.vec2ang(coordinates)) * 180.0 / math.pi
    #             angles = angles.T

    #             for i in range(len(batch)):
    #                 output.write("<a href='" + hipster_url + "/" + title + "/jpg/")
    #                 output.write(str(metadata["simulation"][i]) + "/")
    #                 output.write(str(metadata["snapshot"][i]) + "/")
    #                 output.write(
    #                     str(metadata["subhalo_id"][i]) + ".jpg' target='_blank'>"
    #                 )
    #                 output.write(
    #                     "<img src='" + hipster_url + "/" + title + "/thumbnails/"
    #                 )
    #                 output.write(str(metadata["simulation"][i]) + "/")
    #                 output.write(str(metadata["snapshot"][i]) + "/")
    #                 output.write(str(metadata["subhalo_id"][i]) + ".jpg'></a>,")

    #                 output.write(str(metadata["simulation"][i]) + ",")
    #                 output.write(str(metadata["snapshot"][i]) + ",")
    #                 output.write(str(metadata["subhalo_id"][i]) + ",")
    #                 output.write("<a href='" + self.project_url + "/api/")
    #                 output.write(str(metadata["simulation"][i]) + "-1/snapshots/")
    #                 output.write(str(metadata["snapshot"][i]) + "/subhalos/")
    #                 output.write(str(metadata["subhalo_id"][i]) + "/")
    #                 output.write("' target='_blank'>" + self.project_url + "</a>,")
    #                 output.write(str(losses[i]) + ",")
    #                 output.write(str(metadata["id"][i]) + ",")
    #                 output.write(str(angles[i, 1]) + ",")
    #                 output.write(str(90.0 - angles[i, 0]) + ",")
    #                 output.write(str(rotations[i]) + ",")
    #                 output.write(str(coordinates[i, 0]) + ",")
    #                 output.write(str(coordinates[i, 1]) + ",")
    #                 output.write(str(coordinates[i, 2]) + "\n")

    # def create_images(self, output_path: Path):
    #     """Writes preview images to disk.

    #     Args:
    #         output_path (Path): The path to the output directory.
    #     """
    #     self.setup("images")

    #     for batch, metadata in self.dataloader_images:
    #         for i, image in enumerate(batch):
    #             image = torch.swapaxes(image, 0, 2)
    #             image = Image.fromarray(
    #                 (numpy.clip(image.numpy(), 0, 1) * 255).astype(numpy.uint8),
    #                 mode="RGB",
    #             )
    #             filepath = output_path / Path(
    #                 metadata["simulation"][i],
    #                 metadata["snapshot"][i],
    #             )
    #             filepath.mkdir(parents=True, exist_ok=True)
    #             filename = filepath / Path(metadata["subhalo_id"][i] + ".jpg")
    #             image.save(filename)

    # def create_thumbnails(self, output_path: Path):
    #     """Writes preview images to disk.

    #     Args:
    #         output_path (Path): The path to the output directory.
    #     """
    #     self.setup("thumbnail_images")

    #     for batch, metadata in self.dataloader_thumbnail_images:
    #         for i, image in enumerate(batch):
    #             image = torch.swapaxes(image, 0, 2)
    #             image = Image.fromarray(
    #                 (numpy.clip(image.numpy(), 0, 1) * 255).astype(numpy.uint8),
    #                 mode="RGB",
    #             )
    #             filepath = output_path / Path(
    #                 metadata["simulation"][i],
    #                 metadata["snapshot"][i],
    #             )
    #             filepath.mkdir(parents=True, exist_ok=True)
    #             filename = filepath / Path(metadata["subhalo_id"][i] + ".jpg")
    #             image.save(filename)
