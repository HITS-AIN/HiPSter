import math
import multiprocessing as mp
import os
import pathlib
from datetime import datetime, timezone
from typing import Callable

import healpy
import numpy as np
import pyarrow.dataset as ds
from PIL import Image

from hipster.html_generator import HTMLGenerator

from .inference import Inference
from .task import Task


class DatasetProjection(Task):
    def __init__(
        self,
        encoder: Inference,
        data_directory: str,
        image_maker: Callable,
        hierarchy: int = 1,
        hips_path: str = "output",
        number_of_workers: int = 1,
        max_order: int = 1,
        hips_id: str = "",
        hips_name: str = "",
        distortion_correction: bool = True,
        catalog_file: str = "",
        **kwargs,
    ):
        """Generates a HiPS tiling following the standard defined in
        https://www.ivoa.net/documents/HiPS/20170519/REC-HIPS-1.0-20170519.pdf

        Args:
            encoder(Inference): Function that encodes the data.
            data_directory (str): The directory containing the data.
            image_maker (callable): Function that generates the image.
            hierarchy (int, optional): Hierarchy of the HiPS tiling. Defaults to 1.
            output_path (str, optional): Output path. Defaults to "output".
            number_of_workers (int, optional): Number of workers. Defaults to 1.
            max_order (int, optional): Maximum order of the HiPS tiling. Defaults to 1.
            hips_id (str, optional): HiPS ID. Defaults to "".
            hips_name (str, optional): HiPS name. Defaults to "".
            distortion_correction (bool, optional): Correction of the distortion of the HiPS tiles. Defaults to True.
            catalog_file (str, optional): Path to the catalog file. Defaults to "".
        """
        super().__init__("DatasetProjection", **kwargs)
        self.encoder = encoder
        self.data_directory = data_directory
        self.image_maker = image_maker
        self.hierarchy = hierarchy
        self.hips_path = hips_path
        self.output_path = os.path.join(self.root_path, hips_path)
        self.number_of_workers = number_of_workers
        self.max_order = max_order
        self.hips_id = hips_id
        self.hips_name = hips_name
        self.distortion_correction = distortion_correction
        self.catalog_file = catalog_file

    def __create_folders(
        self,
        max_order: int,
    ):
        """Creates all folders and sub-folders to store the HiPS tiles.

        Args:
            max_order (int): Maximum order of the HiPS tiling.
        """
        path1 = pathlib.Path(self.output_path)
        path1.mkdir(parents=True, exist_ok=True)
        for i in range(max_order + 1):
            path2 = path1 / f"Norder{i}"
            path2.mkdir(parents=True, exist_ok=True)
            for j in range(int(math.floor(12 * 4**i / 10000)) + 1):
                path3 = path2 / f"Dir{j * 10000}"
                path3.mkdir(parents=True, exist_ok=True)

    def __write_properties(self) -> None:
        """Writes the properties of the HiPS data to a file."""
        with open(
            os.path.join(self.output_path, "properties"), "w", encoding="utf-8"
        ) as f:
            f.write(f"""
creator_did          = ivo://HITS/hipster
obs_title            = {self.hips_name}
dataproduct_type     = image
dataproduct_subtype  = color
hips_version         = 1.4
hips_creation_date   = {datetime.now(tz=timezone.utc).isoformat()}
hips_status          = public master clonable
hips_tile_format     = jpeg
hips_order           = {self.max_order}
hips_order_min       = 0
hips_tile_width      = {self.hierarchy * self.image_maker.figsize_in_pixel}
hips_frame           = equatorial
""")

    def __calculate_healpix_cells(
        self,
        catalog: np.ndarray,
        numbers: range,
        order: int,
        pixels: range,
    ):
        healpix_cells = {}  # create an extra map to quickly find images in a cell
        for pixel in pixels:
            healpix_cells[pixel] = []  # create empty lists for each cell
        for number in numbers:
            pixel = healpy.vec2pix(
                2**order,
                catalog[number][4],
                catalog[number][5],
                catalog[number][6],
                nest=True,
            )
            if pixel in healpix_cells:
                healpix_cells[pixel].append(int(number))
        return healpix_cells

    def __embed_tile(self, dataset, catalog, order, pixel, hierarchy, idx):
        if hierarchy <= 1:
            if len(idx) == 0:
                data = np.ones((3, self.output_size, self.output_size))
                data[0] = data[0] * 77.0 / 255.0  # deep purple
                data[1] = data[1] * 0.0 / 255.0
                data[2] = data[2] * 153.0 / 255.0
                data = np.swapaxes(data, 0, 2)
            else:
                vector = healpy.pix2vec(2**order, pixel, nest=True)
                distances = np.sum(
                    np.square(catalog[np.array(idx)][:, 4:7] - vector), axis=1
                )
                best = idx[np.argmin(distances)]
                data = dataset[int(catalog[best][0])]["image"]
                data = functional.rotate(data, catalog[best][3], expand=False)
                data = functional.center_crop(
                    data, [self.crop_size, self.crop_size]
                )  # crop
                data = self.__project_data(data, order, pixel)
            return data
        healpix_cells = self.__calculate_healpix_cells(
            catalog, idx, order + 1, range(pixel * 4, pixel * 4 + 4)
        )
        q1 = self.embed_tile(
            dataset,
            catalog,
            order + 1,
            pixel * 4,
            hierarchy / 2,
            healpix_cells[pixel * 4],
        )
        q2 = self.embed_tile(
            dataset,
            catalog,
            order + 1,
            pixel * 4 + 1,
            hierarchy / 2,
            healpix_cells[pixel * 4 + 1],
        )
        q3 = self.embed_tile(
            dataset,
            catalog,
            order + 1,
            pixel * 4 + 2,
            hierarchy / 2,
            healpix_cells[pixel * 4 + 2],
        )
        q4 = self.embed_tile(
            dataset,
            catalog,
            order + 1,
            pixel * 4 + 3,
            hierarchy / 2,
            healpix_cells[pixel * 4 + 3],
        )
        result = np.ones((q1.shape[0] * 2, q1.shape[1] * 2, 3))
        result[: q1.shape[0], : q1.shape[1]] = q1
        result[q1.shape[0] :, : q1.shape[1]] = q2
        result[: q1.shape[0], q1.shape[1] :] = q3
        result[q1.shape[0] :, q1.shape[1] :] = q4
        return result

    def __create_embeded_tile(self, dataset, catalog, healpix_cells, i, range_j):
        for j in range_j:
            data = self.__embed_tile(
                dataset, catalog, i, j, self.hierarchy, healpix_cells[j]
            )
            image = Image.fromarray(
                (np.clip(data.detach().numpy(), 0, 1) * 255).astype(np.uint8)
            )
            image.save(
                os.path.join(
                    self.output_path,
                    "Norder" + str(i),
                    "Dir" + str(int(math.floor(j / 10000)) * 10000),
                    "Npix" + str(j) + ".jpg",
                )
            )

    def execute(self) -> None:
        """Generates the HiPS tiles."""

        print(f"Executing task: {self.name}")
        self.__create_folders(self.max_order)

        dataset = ds.dataset(self.data_directory, format="parquet")

        print("Loading catalog...")
        catalog = np.genfromtxt(
            self.catalog_file,
            delimiter=",",
            skip_header=1,
            usecols=[6, 7, 8, 9, 10, 11, 12],
        )  # id, RA2000, DEC2000, rotation, x, y, z

        for i in range(self.max_order + 1):

            healpix_cells = self.__calculate_healpix_cells(
                catalog, range(catalog.shape[0]), i, range(12 * 4**i)
            )

            if self.number_of_workers == 1:
                self.__create_embeded_tile(
                    dataset, catalog, healpix_cells, i, range(12 * 4**i)
                )
            else:
                # process_map(_foo, range(0, 30), max_workers=2)

                mypool = []
                for t in range(self.number_of_workers):
                    mypool.append(
                        mp.Process(
                            target=self.__create_embeded_tile,
                            args=(
                                dataset,
                                catalog,
                                healpix_cells,
                                i,
                                range(
                                    t * 12 * 4**i // self.number_of_workers,
                                    (t + 1) * 12 * 4**i // self.number_of_workers,
                                ),
                            ),
                        )
                    )
                    mypool[-1].start()
                for process in mypool:
                    process.join()

        # Write the properties of the HiPS data to a file
        # This must be done after the tiles are generated
        # to ensure the tile size is correct
        self.__write_properties()

    def register(self, html_generator: HTMLGenerator) -> None:
        """Register the HiPS generator to the HTML generator."""
        html_generator.add_image_layer(
            html_generator.ImageLayer(
                hips_id=self.hips_id,
                hips_name=self.hips_name,
                hips_url=f"{html_generator.url}/{self.hips_path}",
                hips_max_order=self.max_order,
            )
        )
