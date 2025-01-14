import math
import multiprocessing as mp
import os

import onnxruntime as ort
from tqdm.contrib.concurrent import process_map


def create_hips_tile(
    ort_encoder: ort.InferenceSession,
    i: int,
    range_j: range,
):
    for j in range_j:
        vectors = torch.zeros(
            (hipster.hierarchy**2, 3), dtype=torch.float32
        )  # prepare vor n*n subtiles
        for sub in range(
            hipster.hierarchy**2
        ):  # calculate coordinates for all n*n subpixels
            vector = healpy.pix2vec(
                2**i * hipster.hierarchy, j * hipster.hierarchy**2 + sub, nest=True
            )
            vectors[sub] = torch.tensor(vector).reshape(1, 3).type(dtype=torch.float32)
        data = model.reconstruct(vectors)
        image = hipster.generate_tile(data, i, j, hipster.hierarchy, 0)
        image = Image.fromarray(
            (numpy.clip(image.detach().numpy(), 0, 1) * 255).astype(numpy.uint8)
        )
        image.save(
            os.path.join(
                hipster.output_folder,
                hipster.title,
                "model",
                "Norder" + str(i),
                "Dir" + str(int(math.floor(j / 10000)) * 10000),
                "Npix" + str(j) + ".jpg",
            )
        )
        print(".", end="", flush=True)


def generate_hips(
    encoder_path: str | os.PathLike,
    max_order: int = 3,
    number_of_workers: int = 1,
):
    """Generates a HiPS tiling following the standard defined in
        https://www.ivoa.net/documents/HiPS/20170519/REC-HIPS-1.0-20170519.pdf

    Args:
        encoder (str | bytes | os.PathLike): Path to the encoder model
        max_order (int, optional): Maximum order of the HiPS tiling. Defaults to 3.
        number_of_workers (int, optional): Number of workers to use. Defaults to 1.
    """
    ort_encoder = ort.InferenceSession(os.fspath(encoder_path))

    for i in range(max_order + 1):
        print(
            "  order "
            + str(i)
            + " ["
            + str(12 * 4**i).rjust(int(math.log10(12 * 4**max_order)) + 1, " ")
            + " tiles]:",
            end="",
            flush=True,
        )
        if number_of_workers == 1:
            create_hips_tile(ort_encoder, i, range(12 * 4**i))
        else:
            # process_map(_foo, range(0, 30), max_workers=2)

            mypool = []
            for t in range(number_of_workers):
                mypool.append(
                    mp.Process(
                        target=create_hips_tile,
                        args=(
                            ort_encoder,
                            i,
                            range(
                                t * 12 * 4**i // number_of_workers,
                                (t + 1) * 12 * 4**i // number_of_workers,
                            ),
                        ),
                    )
                )
                mypool[-1].start()
            for process in mypool:
                process.join()
