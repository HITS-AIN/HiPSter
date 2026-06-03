import math
import multiprocessing as mp
import os
import pathlib
from datetime import datetime, timezone
from typing import Callable

import healpy
import numpy as np
from PIL import Image

from hipster.html_generator import HTMLGenerator

from .inference import Inference
from .task import Task

# from tqdm.contrib.concurrent import process_map


class HiPSGenerator(Task):
    def __init__(
        self,
        decoder: Inference,
        image_maker: Callable,
        hierarchy: int = 1,
        hips_path: str = "output",
        number_of_workers: int = 1,
        max_order: int = 1,
        hips_id: str = "",
        hips_name: str = "",
        distortion_correction: bool = True,
        **kwargs,
    ):
        """Generates a HiPS tiling following the standard defined in
        https://www.ivoa.net/documents/HiPS/20170519/REC-HIPS-1.0-20170519.pdf

        Args:
            decoder(Inference): Function that reconstructs the data.
            image_maker (callable): Function that generates the image.
            hierarchy (int, optional): Hierarchy of the HiPS tiling. Defaults to 1.
            output_path (str, optional): Output path. Defaults to "output".
            number_of_workers (int, optional): Number of workers. Defaults to 1.
            max_order (int, optional): Maximum order of the HiPS tiling. Defaults to 1.
            hips_id (str, optional): HiPS ID. Defaults to "".
            hips_name (str, optional): HiPS name. Defaults to "".
            distortion_correction (bool, optional): Correction of the distortion of the HiPS tiles. Defaults to True.
        """
        super().__init__("HiPSGenerator", **kwargs)
        self.decoder = decoder
        self.image_maker = image_maker
        self.hierarchy = hierarchy
        self.hips_path = hips_path
        self.output_path = os.path.join(self.root_path, hips_path)
        self.number_of_workers = number_of_workers
        self.max_order = max_order
        self.hips_id = hips_id
        self.hips_name = hips_name
        self.distortion_correction = distortion_correction

    def __create_hips_tile(
        self,
        i: int,
        range_j: range,
    ):
        for j in range_j:
            vectors = np.zeros((self.hierarchy**2, 3), dtype=np.float32)
            for sub in range(self.hierarchy**2):
                vectors[sub] = healpy.pix2vec(2**i * self.hierarchy, j * self.hierarchy**2 + sub, nest=True)
            recon = self.decoder(vectors)
            image = self.generate_tile(recon, i, j, self.hierarchy, 0)
            image = Image.fromarray(image)
            image.save(
                os.path.join(
                    self.output_path,
                    "Norder" + str(i),
                    "Dir" + str(int(math.floor(j / 10000)) * 10000),
                    "Npix" + str(j) + ".jpg",
                )
            )

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

    def __calculate_pixels(self, matrix, pixel):
        """Calculates the pixel values for the HiPS tiling."""
        size = matrix.shape[0]
        if size > 1:
            matrix[:size//2,:size//2] = self.__calculate_pixels(matrix[:size//2,:size//2], pixel*4)
            matrix[size//2:,:size//2] = self.__calculate_pixels(matrix[size//2:,:size//2], pixel*4+1)
            matrix[:size//2,size//2:] = self.__calculate_pixels(matrix[:size//2,size//2:], pixel*4+2)
            matrix[size//2:,size//2:] = self.__calculate_pixels(matrix[size//2:,size//2:], pixel*4+3)
        else:
            matrix = pixel
        return matrix

    def __correct_distortion(self, data, order, pixel):
        """Corrects the distortion of the HiPS tiles."""
        size = data.shape[0]
        healpix_pixel = np.zeros((size, size), dtype=np.int64)
        healpix_pixel = self.__calculate_pixels(healpix_pixel, pixel)

        center_theta, center_phi = healpy.pix2ang(2**order, pixel, nest=True)  # theta 0...180 phi 0...360
        max_theta = max_phi = 2 * math.pi / (4 * 2**order) / 2

        # Vectorised healpy call — healpy is CPU-only, but accepts an array of pixels
        target_theta, target_phi = healpy.pix2ang(
            2**order * size, healpix_pixel.ravel(), nest=True
        )
        target_theta = target_theta.reshape(size, size)
        target_phi = target_phi.reshape(size, size)

        # Move array operations to GPU if CuPy is available, otherwise fall back to NumPy
        use_gpu = False
        try:
            import cupy as xp
            target_theta = xp.asarray(target_theta)
            target_phi = xp.asarray(target_phi)
            data = xp.asarray(data)
            use_gpu = True
        except ImportError:
            xp = np

        delta_theta = target_theta - center_theta
        delta_phi = xp.where(
            (center_phi == 0) & (target_phi > math.pi),
            (target_phi - 2 * math.pi) * xp.sin(target_theta),
            (target_phi - center_phi) * xp.sin(target_theta),
        )

        target_x = (size // 2 + delta_phi / max_phi * (size // 2 - 1)).astype(xp.int32)
        target_y = (size // 2 + delta_theta / max_theta * (size // 2 - 1)).astype(xp.int32)

        valid = (target_x >= 0) & (target_y >= 0) & (target_x < size) & (target_y < size)
        xs, ys = xp.where(valid)

        result = xp.zeros((size, size, 3), dtype=xp.uint8)
        result[xs, ys] = data[target_x[xs, ys], target_y[xs, ys]]

        return result.get() if use_gpu else result

    def generate_tile(self, data, order, pixel, hierarchy, index):
        """Construct the hierarchical tiling of the HiPS."""
        if hierarchy <= 1:
            image = self.image_maker(data[index])
            if self.distortion_correction:
                image = self.__correct_distortion(image, order, pixel)
            return image

        q1 = self.generate_tile(data, order + 1, pixel * 4, hierarchy / 2, index * 4)
        q2 = self.generate_tile(data, order + 1, pixel * 4 + 1, hierarchy / 2, index * 4 + 1)
        q3 = self.generate_tile(data, order + 1, pixel * 4 + 2, hierarchy / 2, index * 4 + 2)
        q4 = self.generate_tile(data, order + 1, pixel * 4 + 3, hierarchy / 2, index * 4 + 3)
        result = np.ndarray((q1.shape[0] * 2, q1.shape[1] * 2, 3), dtype=np.uint8)
        result[: q1.shape[0], : q1.shape[1]] = q1
        result[q1.shape[0] :, : q1.shape[1]] = q2
        result[: q1.shape[0], q1.shape[1] :] = q3
        result[q1.shape[0] :, q1.shape[1] :] = q4
        return result

    def write_properties(self) -> None:
        """Writes the properties of the HiPS data to a file."""
        with open(os.path.join(self.output_path, "properties"), "w", encoding="utf-8") as f:
            f.write(
                f"""
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
"""
            )

    def execute(self) -> None:
        """Generates the HiPS tiles."""

        print(f"Executing task: {self.name}")
        self.__create_folders(self.max_order)

        for i in range(self.max_order + 1):
            if self.number_of_workers == 1:
                self.__create_hips_tile(i, range(12 * 4**i))
            else:
                # process_map(_foo, range(0, 30), max_workers=2)

                mypool = []
                for t in range(self.number_of_workers):
                    mypool.append(
                        mp.Process(
                            target=self.__create_hips_tile,
                            args=(
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
        self.write_properties()

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
