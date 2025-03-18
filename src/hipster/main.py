from typing import Optional

from jsonargparse import auto_cli

from hipster.hips_generator import HiPSGenerator


def main(
    url: str = "http://localhost:8083",
    title: str = "gaia",
    max_order: int = 4,
    hips: Optional[HiPSGenerator] = None,
):
    """
    Main function to generate HiPS data.

    Args:
        url (str): The URL of the HiPS server.
        title (str): The title of the HiPS data.
        max_order (int): The maximum order of the HiPS tiling.
        hips (Optional[HiPSGenerator]): An instance of HiPSGenerator.
    """
    if hips is not None:
        hips(max_order=max_order)


if __name__ == "__main__":
    auto_cli(main)
